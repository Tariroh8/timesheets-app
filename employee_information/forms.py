from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Role, Department, Position, Timesheet, DailyEntry  # Ensure you import Department and Position

from django.contrib.auth.forms import AuthenticationForm

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Department, Position, Role
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit

class CustomUserCreationForm(UserCreationForm):
    firstname = forms.CharField(max_length=30, label='First Name')
    middlename = forms.CharField(max_length=30, required=False, label='Middle Name')
    lastname = forms.CharField(max_length=30, label='Last Name')
    gender = forms.CharField(max_length=10, required=False, label='Gender')
    dob = forms.DateField(required=False, label='Date of Birth', widget=forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD'}))
    contact = forms.CharField(max_length=15, label='Contact Number')
    address = forms.CharField(widget=forms.Textarea, label='Address')
    email = forms.EmailField(label='Email')
    department = forms.ModelChoiceField(queryset=Department.objects.all(), label='Department')
    position = forms.ModelChoiceField(queryset=Position.objects.all(), label='Position')
    role = forms.ModelChoiceField(queryset=Role.objects.all(), label='Role')

    class Meta:
        model = CustomUser
        fields = [
            'username', 'firstname', 'middlename', 'lastname', 
            'gender', 'dob', 'contact', 'address', 'email', 
            'password1', 'password2', 'department', 'position', 'role'
        ]

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'username',
            'firstname',
            'middlename',
            'lastname',
            'gender',
            'dob',
            'contact',
            'address',
            'email',
            'department',
            'position',
            'role',
            'password1',  # Include password1
            'password2',  # Include password2
            Submit('submit', 'Sign Up')  # Add the submit button in the layout
        )

# employee_information/forms.py


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        label='',  
        widget=forms.TextInput(attrs={
            'placeholder': 'Username or Email',
            'class': 'form-control'  # Add Bootstrap class for styling
        })
    )
    password = forms.CharField(
        label='', 
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Password',
            'class': 'form-control'  # Add Bootstrap class for styling
        })
    )

    def __init__(self, *args, **kwargs):
        super(CustomLoginForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'username',
            'password',
            Submit('submit', 'Login', css_class='btn btn-primary btn-block')  # Responsive submit button
        )


class TimesheetForm(forms.ModelForm):
    class Meta:
        model = Timesheet
        fields = ['user', 'month']

    def __init__(self, *args, **kwargs):
        super(TimesheetForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'user',  # User field will be displayed but disabled
            'month',
            Submit('submit', 'Submit Timesheet')  # Add a submit button
        )

        # Disable the user field
        self.fields['user'].widget.attrs['disabled'] = 'disabled' 
        
class DailyEntryForm(forms.ModelForm):
    class Meta:
        model = DailyEntry
        fields = ['date', 'time_in', 'time_out']