from django.contrib.auth.models import AbstractUser
from datetime import datetime, timedelta
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ValidationError

class Role(models.Model):
    ROLE_CHOICES = [
        ('employee', 'Employee'),
        ('supervisor', 'Supervisor'),
        ('finance_manager', 'FinanceManager'),
        ('hr', 'HR'),
    ]

    name = models.CharField(max_length=20, choices=ROLE_CHOICES, unique=True)

    def __str__(self):
        return self.name

# Create your models here.
class Department(models.Model):
    name = models.TextField() 
    description = models.TextField() 
    status = models.IntegerField() 
    date_added = models.DateTimeField(default=timezone.now) 
    date_updated = models.DateTimeField(auto_now=True) 

    def __str__(self):
        return self.name

class Position(models.Model):
    name = models.TextField() 
    description = models.TextField() 
    status = models.IntegerField() 
    date_added = models.DateTimeField(default=timezone.now) 
    date_updated = models.DateTimeField(auto_now=True) 

    def __str__(self):
        return self.name



class CustomUser(AbstractUser):
    firstname = models.CharField(max_length=30)
    middlename = models.CharField(max_length=30, blank=True, null=True)
    lastname = models.CharField(max_length=30)
    gender = models.CharField(max_length=10, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    contact = models.CharField(max_length=15)
    address = models.TextField()
    email = models.EmailField(unique=True)
    department = models.ForeignKey('Department', on_delete=models.CASCADE,  blank=True, null=True)
    position = models.ForeignKey('Position', on_delete=models.CASCADE,  blank=True, null=True)
    date_hired = models.DateField(blank=True, null=True)
    date_added = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.pk is not None:  # Checking if the user already exists
            original = CustomUser.objects.get(pk=self.pk)
            if original.role != self.role:
                raise ValueError("Role cannot be changed after user creation.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.firstname} {self.middlename or ''} {self.lastname}"


class Employees(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    date_hired = models.DateField()

    def __str__(self):
        return f"{self.user.firstname} {self.user.lastname}"

class Supervisor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    date_hired = models.DateField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"{self.user.firstname} {self.user.lastname}"

class FinanceManager(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    date_hired = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.firstname} {self.user.lastname}"

class Hr(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    date_hired = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.firstname} {self.user.lastname}"



class Timesheet(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    month = models.DateField()
    supervisor_approved = models.BooleanField(default=False)
    finance_manager_approved = models.BooleanField(default=False)
    hr_approved = models.BooleanField(default=False)
    approved_at = models.DateTimeField(null=True, blank=True)

    def create_daily_entries(self):
        # Get the first and last day of the month
        start_date = self.month.replace(day=1)
        next_month = start_date.replace(day=28) + timedelta(days=4)  # This will never fail
        end_date = next_month - timedelta(days=next_month.day)  # Last day of the month

        # Create DailyEntry for each day of the month
        for single_date in (start_date + timedelta(n) for n in range((end_date - start_date).days + 1)):
            DailyEntry.objects.create(
                timesheet=self,
                date=single_date
            )

    def save(self, *args, **kwargs):
        # Check if a timesheet for this user and month already exists
        existing_timesheet = Timesheet.objects.filter(
            user=self.user,
            month__year=self.month.year,
            month__month=self.month.month
        ).exclude(id=self.id).first() 

        if existing_timesheet:
            return  # Do not create a new instance; simply return

        super().save(*args, **kwargs)  # Call the original save method
        self.create_daily_entries()  # Create daily entries after saving the Timesheet

    def approve_by_supervisor(self):
        print(f"Approving timesheet ID: {self.id} for user: {self.user.username}")
        self.supervisor_approved = True
        self.approved_at = timezone.now()  # Set approved timestamp
        #self.save()  # This should save the updated status to the database
        print(f"Timesheet ID: {self.id} approved. Supervisor Approved Statussss: {self.supervisor_approved}")

    def total_hours(self):
        # Calculate total hours from all related DailyEntry instances
        total = sum(entry.total_hours for entry in self.daily_entries.all())
        return total

    def count_reported_days(self):
        # Count the number of daily entries where time_in is not null
        reported_days = self.daily_entries.filter(time_in__isnull=False).count()
        return reported_days

    def count_non_weekend_absent_days(self):
        # Count the number of absent days (time_in is null) that are not on weekends
        absent_days = 0
        # Get the first and last day of the month for filtering
        start_date = self.month.replace(day=1)
        next_month = start_date.replace(day=28) + timedelta(days=4)  # This will never fail
        end_date = next_month - timedelta(days=next_month.day)  # Last day of the month

        # Iterate through daily entries that are within the current month
        for entry in self.daily_entries.filter(date__range=[start_date, end_date]):
            if entry.time_in is None:  # Check if time_in is null
                if entry.date.weekday() < 5:  # Check if the day is not Saturday (5) or Sunday (6)
                    absent_days += 1
        return absent_days


    def approve_by_supervisor(self):
        print(f"Approving timesheet ID: {self.id} for user: {self.user.username}")
        self.supervisor_approved = True
        self.approved_at = timezone.now()  # Set approved timestamp
        # Save directly to avoid issues with existing timesheet check
        Timesheet.objects.filter(id=self.id).update(supervisor_approved=True, approved_at=self.approved_at)  # Use update to bypass save method
        print(f"Timesheet ID: {self.id} approved. Supervisor Approved Statussss: {self.supervisor_approved}")

    def approve_by_finance_manager(self):
        print(f"Approving timesheet ID: {self.id} for user: {self.user.username}")
        self.finance_manager_approved = True
        self.approved_at = timezone.now()  # Set approved timestamp
        #Timesheet.objects.filter(id=self.id).update(finance_manager_approved=True, approved_at=self.approved_at)  # Use update to bypass save method
        print(f"Timesheet ID: {self.id} approved. Finance Approved Status: {self.finance_manager_approved}")
        

    def approve_by_hr(self):
        if self.finance_manager_approved:  # Ensure it has been approved by finance manager first
            self.hr_approved = True
            #self.save()

    def __str__(self):
        return f"Timesheet for {self.user.username} - {self.month.strftime('%B %Y')}"


class DailyEntry(models.Model):
    timesheet = models.ForeignKey(Timesheet, related_name='daily_entries', on_delete=models.CASCADE)
    
    date = models.DateField()
    activity = models.CharField(max_length=30, blank=True, null=True)
    time_in = models.TimeField(blank=True, null=True)
    time_out = models.TimeField(blank=True, null=True)

    @property 
    def total_hours(self):
        if self.time_in and self.time_out:
            start = datetime.combine(self.date, self.time_in)
            end = datetime.combine(self.date, self.time_out)
            return (end - start).total_seconds() / 3600  # Convert seconds to hours
        return 0

    def __str__(self):
        return f"Entry for {self.date} - {self.timesheet.user.username}"



