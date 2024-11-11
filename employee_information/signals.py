from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from .models import CustomUser, Employees, Supervisor, FinanceManager, Hr

@receiver(post_save, sender=CustomUser)
def create_employee_profile(sender, instance, created, **kwargs):
    if created and instance.role and instance.role.name == 'Employee':
        print('**********************************************************************************************************************************************')
        print(f"Creating employee profile for {instance.username}")
        Employees.objects.create(user=instance, date_hired=timezone.now())

@receiver(post_save, sender=CustomUser)
def save_employee_profile(sender, instance, **kwargs):
    if instance.role and instance.role.name == 'Employee':
        try:
            employee_profile = Employees.objects.get(user=instance)
            # Update fields as necessary
            employee_profile.date_hired = instance.date_hired if instance.date_hired else timezone.now()
            employee_profile.save()
            print(f"Updated employee profile for {instance.username}")
        except Employees.DoesNotExist:
            print(f"No existing employee profile found for {instance.username}, will be created.")
            Employees.objects.create(user=instance, date_hired=timezone.now())  # Create if not found

# Signal to create a supervisor profile
@receiver(post_save, sender=CustomUser)
def create_supervisor_profile(sender, instance, created, **kwargs):
    if created and instance.role and instance.role.name == 'supervisor':
        print('**********************************************************************************************************************************************')
        print(f"Creating supervisor profile for {instance.username}")
        Supervisor.objects.create(user=instance)

# Signal to save or update the supervisor profile
@receiver(post_save, sender=CustomUser)
def save_supervisor_profile(sender, instance, **kwargs):
    if instance.role and instance.role.name == 'supervisor':
        try:
            supervisor_profile = Supervisor.objects.get(user=instance)
            # Update fields as necessary (add any specific fields to update)
            supervisor_profile.save()
            print(f"Updated supervisor profile for {instance.username}")
        except Supervisor.DoesNotExist:
            print(f"No existing supervisor profile found for {instance.username}, will be created.")
            Supervisor.objects.create(user=instance) 

# Signal to create a Financial Manager profile
@receiver(post_save, sender=CustomUser)
def create_supervisor_profile(sender, instance, created, **kwargs):
    if created and instance.role and instance.role.name == 'finance_manager':
        print('**********************************************************************************************************************************************')
        print(f"Creating finance_manager profile for {instance.username}")
        FinanceManager.objects.create(user=instance)

# Signal to save or update the finance manager profile
@receiver(post_save, sender=CustomUser)
def save_supervisor_profile(sender, instance, **kwargs):
    if instance.role and instance.role.name == 'finance_manager':
        try:
            fm_profile = FinanceManager.objects.get(user=instance)
            # Update fields as necessary (add any specific fields to update)
            fm_profile.save()
            print(f"Updated finance_manager profile for {instance.username}")
        except Supervisor.DoesNotExist:
            print(f"No existing finance_manager profile found for {instance.username}, will be created.")
            FinanceManager.objects.create(user=instance) 


# Signal to create a hr profile
@receiver(post_save, sender=CustomUser)
def create_hr_profile(sender, instance, created, **kwargs):
    if created and instance.role and instance.role.name == 'hr':
        print('**********************************************************************************************************************************************')
        print(f"Creating hr profile for {instance.username}")
        Hr.objects.create(user=instance)

# Signal to save or update the hr profile
@receiver(post_save, sender=CustomUser)
def save_hr_profile(sender, instance, **kwargs):
    if instance.role and instance.role.name == 'hr':
        try:
            hr_profile = Hr.objects.get(user=instance)
            # Update fields as necessary (add any specific fields to update)
            hr_profile.save()
            print(f"Updated hr profile for {instance.username}")
        except Hr.DoesNotExist:
            print(f"No existing hr profile found for {instance.username}, will be created.")
            Hr.objects.create(user=instance)