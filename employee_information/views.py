from django.shortcuts import redirect, render
from django.http import HttpResponse
from employee_information.models import Department,Employees, Role, Timesheet, DailyEntry
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
import json
from .forms import CustomUserCreationForm, CustomLoginForm, TimesheetForm, DailyEntryForm

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404 
from django.contrib import messages
from django.utils import timezone




"""employees = [

    {
        'name':"John D Smith",
        'contact':'09123456789',
        'address':'Sample Address only'
    },{
        'name':"Claire C Blake",
        'contact':'09456123789',
        'address':'Sample Address2 only'
    }

]"""
# Login
def landing_page(request):
    return render(request, 'employee_information/landing_page.html')


def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # Create user but don't save to the database yet
            user.role = form.cleaned_data['role']  # Assign the selected role
            user.save()  # Now save the user
            login(request, user)  # Log the user in after signup
            return redirect('create_timesheet')  # Redirect to a home page or dashboard
    else:
        form = CustomUserCreationForm()
    return render(request, 'employee_information/signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)

                # Debugging output to check the user's role
                print(f"Logged in user: {user.username}, Role: {user.role}")

                # Check user role and redirect accordingly
                if user.role.name == 'supervisor':
                    
                    print("Redirecting to supervisor dashboard.")
                    return redirect('supervisor_dashboard')  # Redirect to the supervisor dashboard
                else:
                    print("Redirecting to create timesheet.")
                    return redirect('create_timesheet')  # Redirect to the standard user page

            else:
                messages.error(request, "Invalid login credentials.")
    else:
        form = CustomLoginForm()

    return render(request, 'employee_information/loginn.html', {'form': form})




@login_required
def create_timesheet(request):
    if request.method == 'POST':
        form = TimesheetForm(request.POST, user=request.user)  # Pass the logged-in user
        if form.is_valid():
            date = form.cleaned_data['month']
            if date:
                # Check for existing timesheet logic
                existing_timesheet = Timesheet.objects.filter(
                    user=request.user,
                    month__year=date.year,
                    month__month=date.month
                ).first()

                if existing_timesheet:
                    messages.info(request, f"A timesheet already exists for {request.user.username} for {existing_timesheet.month.strftime('%B %Y')}.")
                    return redirect('timesheet_detail', pk=existing_timesheet.pk)
                else:
                    # Create a new Timesheet instance
                    timesheet = Timesheet(user=request.user, month=date)
                    timesheet.save()
                    messages.success(request, "Timesheet created successfully.")
                    return redirect('timesheet_detail', pk=timesheet.pk)
            else:
                messages.error(request, "Invalid date provided.")
    else:
        form = TimesheetForm(user=request.user)  # Pass the logged-in user on GET

    return render(request, 'employee_information/create_timesheet.html', {
        'form': form,
        'user': request.user
    })


@login_required
def timesheet_detail(request, pk):
    timesheet = get_object_or_404(Timesheet, pk=pk)
    daily_entries = timesheet.daily_entries.all()

    if request.method == 'POST':
        for entry in daily_entries:
            time_in = request.POST.get(f'time_in_{entry.pk}')
            time_out = request.POST.get(f'time_out_{entry.pk}')
            activity = request.POST.get(f'activity_{entry.pk}')  # Get the activity input
            
            if time_in and time_out:
                entry.time_in = time_in
                entry.time_out = time_out
            if activity:  # Update activity if provided
                entry.activity = activity
            
            entry.save()
        
        messages.success(request, "Daily entries updated successfully.")
        return redirect('timesheet_detail', pk=timesheet.pk)

    return render(request, 'employee_information/timesheet_detail.html', {
        'timesheet': timesheet,
        'daily_entries': daily_entries,
    })


@login_required
def add_daily_entry(request, timesheet_pk):
    timesheet = Timesheet.objects.get(pk=timesheet_pk)
    if request.method == 'POST':
        form = DailyEntryForm(request.POST)
        if form.is_valid():
            daily_entry = form.save(commit=False)
            daily_entry.timesheet = timesheet
            daily_entry.save()
            return redirect('timesheet_detail', pk=timesheet.pk)
    else:
        form = DailyEntryForm()
    return render(request, 'employee_information/add_daily_entry.html', {
        'form': form,
        'timesheet': timesheet,
    })

@login_required
def supervisor_dashboard(request):
    # Get the current month and year
    today = timezone.now()
    current_month = today.month
    current_year = today.year

    # Get month and year from GET parameters if provided
    month = request.GET.get('month', current_month)
    year = request.GET.get('year', current_year)

    # Filter timesheets for the specified month and year
    timesheets = Timesheet.objects.filter(month__year=year, month__month=month)

    # Format the date for display
    formatted_date = timezone.datetime(year, month, 1).strftime('%B %Y')

    # Prepare the timesheets with formatted month
    formatted_timesheets = [
        {
            'timesheet': timesheet,
            'formatted_month': timesheet.month.strftime('%B %Y')
        }
        for timesheet in timesheets
    ]

    # Calculate totals
    total_timesheets = len(formatted_timesheets)
    approved_timesheets = sum(1 for item in formatted_timesheets if item['timesheet'].supervisor_approved)
    not_approved_timesheets = total_timesheets - approved_timesheets

    # Render the template with context
    return render(request, 'employee_information/sdashboard.html', {
        'timesheets': formatted_timesheets,
        'formatted_date': formatted_date,
        'total_timesheets': total_timesheets,
        'approved_timesheets': approved_timesheets,
        'not_approved_timesheets': not_approved_timesheets,
        'current_month': current_month,
        'current_year': current_year,
    })
    
@login_required
def financial_manager_dashboard(request):
    # Get the current month and year
    today = timezone.now()
    current_month = today.month
    current_year = today.year

    # Filter timesheets that have been approved by the supervisor
    timesheets = Timesheet.objects.filter(
        month__year=current_year,
        month__month=current_month,
        supervisor_approved=True  # Only include timesheets that are approved
    )

    # Format the date for display
    formatted_date = today.strftime('%B %Y')

    # Prepare the timesheets with formatted month
    formatted_timesheets = [
        {
            'timesheet': timesheet,
            'formatted_month': timesheet.month.strftime('%B %Y')
        }
        for timesheet in timesheets
    ]

    total_timesheets = len(formatted_timesheets)
    approved_timesheets = sum(1 for item in formatted_timesheets if item['timesheet'].finance_manager_approved)
    not_approved_timesheets = total_timesheets - approved_timesheets

    return render(request, 'employee_information/financial_manager_dashboard.html', {
        'timesheets': formatted_timesheets,
        'formatted_date': formatted_date,  # Pass the formatted date to the template
        'total_timesheets': total_timesheets,
        'approved_timesheets': approved_timesheets,
        'not_approved_timesheets': not_approved_timesheets,
    })


@login_required
def supervisor_approve_timesheet(request, timesheet_id):
    # Get the timesheet instance
    timesheet = get_object_or_404(Timesheet, id=timesheet_id)

    print(f"Attempting to approve timesheet ID: {timesheet.id} for user: {timesheet.user.username}")

    if request.method == "POST":
        timesheet.approve_by_supervisor()  # Use the model method to approve

        print(f"Timesheet ID: {timesheet.id} approved by supervisor.")
        print(f"Supervisor Approved Status: {timesheet.supervisor_approved}")  # Should be True
        return redirect('supervisor_dashboard')  # Redirect to the dashboard after approval

@login_required
def financial_manager_approve_timesheet(request, timesheet_id):
    # Get the timesheet instance
    timesheet = get_object_or_404(Timesheet, id=timesheet_id)

    print(f"Attempting to approve timesheet ID: {timesheet.id} for user: {timesheet.user.username}")

    if request.method == "POST":
        timesheet.approve_by_finance_manager()  # Use the model method to approve

        print(f"Timesheet ID: {timesheet.id} approved by f manager.")
        print(f"Supervisor Approved Status: {timesheet.finance_manager_approved}")  # Should be True
        
        return redirect('financial_manager_dashboard')


'''
def login_user(request):
    logout(request)
    resp = {"status":'failed','msg':''}
    username = ''
    password = ''
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                resp['status']='success'
            else:
                resp['msg'] = "Incorrect username or password"
        else:
            resp['msg'] = "Incorrect username or password"
    return HttpResponse(json.dumps(resp),content_type='application/json')

#Logout
def logoutuser(request):
    logout(request)
    return redirect('/')

# Create your views here.
@login_required
def home(request):
    context = {
        'page_title':'Home',
        'employees':employees,
        'total_department':len(Department.objects.all()),
        'total_position':len(Position.objects.all()),
        'total_employee':len(Employees.objects.all()),
    }
    return render(request, 'employee_information/home.html',context)


def about(request):
    context = {
        'page_title':'About',
    }
    return render(request, 'employee_information/about.html',context)

# Departments
@login_required
def departments(request):
    department_list = Department.objects.all()
    context = {
        'page_title':'Departments',
        'departments':department_list,
    }
    return render(request, 'employee_information/departments.html',context)
@login_required
def manage_departments(request):
    department = {}
    if request.method == 'GET':
        data =  request.GET
        id = ''
        if 'id' in data:
            id= data['id']
        if id.isnumeric() and int(id) > 0:
            department = Department.objects.filter(id=id).first()
    
    context = {
        'department' : department
    }
    return render(request, 'employee_information/manage_department.html',context)

@login_required
def save_department(request):
    data =  request.POST
    resp = {'status':'failed'}
    try:
        if (data['id']).isnumeric() and int(data['id']) > 0 :
            save_department = Department.objects.filter(id = data['id']).update(name=data['name'], description = data['description'],status = data['status'])
        else:
            save_department = Department(name=data['name'], description = data['description'],status = data['status'])
            save_department.save()
        resp['status'] = 'success'
    except:
        resp['status'] = 'failed'
    return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
def delete_department(request):
    data =  request.POST
    resp = {'status':''}
    try:
        Department.objects.filter(id = data['id']).delete()
        resp['status'] = 'success'
    except:
        resp['status'] = 'failed'
    return HttpResponse(json.dumps(resp), content_type="application/json")

# Positions
@login_required
def positions(request):
    position_list = Position.objects.all()
    context = {
        'page_title':'Positions',
        'positions':position_list,
    }
    return render(request, 'employee_information/positions.html',context)
@login_required
def manage_positions(request):
    position = {}
    if request.method == 'GET':
        data =  request.GET
        id = ''
        if 'id' in data:
            id= data['id']
        if id.isnumeric() and int(id) > 0:
            position = Position.objects.filter(id=id).first()
    
    context = {
        'position' : position
    }
    return render(request, 'employee_information/manage_position.html',context)

@login_required
def save_position(request):
    data =  request.POST
    resp = {'status':'failed'}
    try:
        if (data['id']).isnumeric() and int(data['id']) > 0 :
            save_position = Position.objects.filter(id = data['id']).update(name=data['name'], description = data['description'],status = data['status'])
        else:
            save_position = Position(name=data['name'], description = data['description'],status = data['status'])
            save_position.save()
        resp['status'] = 'success'
    except:
        resp['status'] = 'failed'
    return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
def delete_position(request):
    data =  request.POST
    resp = {'status':''}
    try:
        Position.objects.filter(id = data['id']).delete()
        resp['status'] = 'success'
    except:
        resp['status'] = 'failed'
    return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
# Employees
def employees(request):
    employee_list = Employees.objects.all()
    context = {
        'page_title':'Employees',
        'employees':employee_list,
    }
    return render(request, 'employee_information/employees.html',context)
@login_required
def manage_employees(request):
    employee = {}
    departments = Department.objects.filter(status = 1).all() 
    positions = Position.objects.filter(status = 1).all() 
    if request.method == 'GET':
        data =  request.GET
        id = ''
        if 'id' in data:
            id= data['id']
        if id.isnumeric() and int(id) > 0:
            employee = Employees.objects.filter(id=id).first()
    context = {
        'employee' : employee,
        'departments' : departments,
        'positions' : positions
    }
    return render(request, 'employee_information/manage_employee.html',context)

@login_required
def save_employee(request):
    data =  request.POST
    resp = {'status':'failed'}
    if (data['id']).isnumeric() and int(data['id']) > 0:
        check  = Employees.objects.exclude(id = data['id']).filter(code = data['code'])
    else:
        check  = Employees.objects.filter(code = data['code'])

    if len(check) > 0:
        resp['status'] = 'failed'
        resp['msg'] = 'Code Already Exists'
    else:
        try:
            dept = Department.objects.filter(id=data['department_id']).first()
            pos = Position.objects.filter(id=data['position_id']).first()
            if (data['id']).isnumeric() and int(data['id']) > 0 :
                save_employee = Employees.objects.filter(id = data['id']).update(code=data['code'], firstname = data['firstname'],middlename = data['middlename'],lastname = data['lastname'],dob = data['dob'],gender = data['gender'],contact = data['contact'],email = data['email'],address = data['address'],department_id = dept,position_id = pos,date_hired = data['date_hired'],salary = data['salary'],status = data['status'])
            else:
                save_employee = Employees(code=data['code'], firstname = data['firstname'],middlename = data['middlename'],lastname = data['lastname'],dob = data['dob'],gender = data['gender'],contact = data['contact'],email = data['email'],address = data['address'],department_id = dept,position_id = pos,date_hired = data['date_hired'],salary = data['salary'],status = data['status'])
                save_employee.save()
            resp['status'] = 'success'
        except Exception:
            resp['status'] = 'failed'
            print(Exception)
            print(json.dumps({"code":data['code'], "firstname" : data['firstname'],"middlename" : data['middlename'],"lastname" : data['lastname'],"dob" : data['dob'],"gender" : data['gender'],"contact" : data['contact'],"email" : data['email'],"address" : data['address'],"department_id" : data['department_id'],"position_id" : data['position_id'],"date_hired" : data['date_hired'],"salary" : data['salary'],"status" : data['status']}))
    return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
def delete_employee(request):
    data =  request.POST
    resp = {'status':''}
    try:
        Employees.objects.filter(id = data['id']).delete()
        resp['status'] = 'success'
    except:
        resp['status'] = 'failed'
    return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
def view_employee(request):
    employee = {}
    departments = Department.objects.filter(status = 1).all() 
    positions = Position.objects.filter(status = 1).all() 
    if request.method == 'GET':
        data =  request.GET
        id = ''
        if 'id' in data:
            id= data['id']
        if id.isnumeric() and int(id) > 0:
            employee = Employees.objects.filter(id=id).first()
    context = {
        'employee' : employee,
        'departments' : departments,
        'positions' : positions
    }
    return render(request, 'employee_information/view_employee.html',context)'''