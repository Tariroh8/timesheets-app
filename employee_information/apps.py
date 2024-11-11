from django.apps import AppConfig

class EmployeeInformationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'employee_information'

    def ready(self):
        # Import the signals module to connect the signal handlers
        import employee_information.signals  # Make sure this matches your app's structure