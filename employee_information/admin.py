from django.contrib import admin
from .models import CustomUser, Role, Department, Position, Employees, Supervisor, FinanceManager, Hr, Timesheet, DailyEntry # Import your models
from django.contrib.auth.admin import UserAdmin

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'firstname', 'lastname', 'email', 'department', 'position', 'role', 'date_hired', 'date_added', 'date_updated')
    list_filter = ('department', 'position', 'role')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('firstname', 'middlename', 'lastname', 'gender', 'dob', 'contact', 'address', 'department', 'position', 'date_hired', 'role')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('firstname', 'middlename', 'lastname', 'gender', 'dob', 'contact', 'address', 'department', 'position', 'date_hired', 'role')}),
    )

# employee_information/admin.py


class TimesheetAdmin(admin.ModelAdmin):
    list_display = ('user', 'month')
    search_fields = ('user__username',)

class DailyEntryAdmin(admin.ModelAdmin):
    list_display = ('timesheet', 'date', 'time_in', 'time_out', 'total_hours')
    list_filter = ('timesheet',)

# Register the CustomUser model with the custom admin class
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Role)  # Register Role if needed
admin.site.register(Department)  # Register Department if needed
admin.site.register(Position) 
admin.site.register(Employees)
admin.site.register(Supervisor)
admin.site.register(FinanceManager) 
admin.site.register(Hr)

admin.site.register(Timesheet, TimesheetAdmin) 
admin.site.register(DailyEntry, DailyEntryAdmin) 
