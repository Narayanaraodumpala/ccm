import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

import django
django.setup()

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command

from revision_be.settings import env


def call_migrations_commands():
    # call_command('collectstatic', verbosity=3, interactive=False)
    call_command('makemigrations', verbosity=3, interactive=False)
    call_command('migrate', verbosity=3, interactive=False)
    return True


def remove_all_migration_scripts():
    for app in settings.USER_APPS:
        if not app.startswith("django.") and app not in settings.THIRD_PARTY_APPS:
            app = app.split('.')[1]
            app_migration_files = os.chdir(f"{settings.BASE_DIR}/apps/{app}/migrations")
            items = os.listdir(app_migration_files)
            for item in items:
                if item.endswith(".py") and not item.startswith('__init__'):
                    os.remove(item)
        else:
            pass
    print(f"[+] All migration files deleted")


def call_create_super_function():
    # Create the super user and sets his password.
    print(f"[+] Now creating super user")
    try:
        User = get_user_model()
        user = User.objects.create(
            first_name='super',
            last_name='admin',
            email='admin@admin.com',
            is_staff=True,
            is_superuser=True,
            user_type='SUPERADMIN'
        )
        user.set_password('pass4321')
        user.save()
        print(f"[+] New Super Admin created.")
    except Exception as e:
        print(f"Error - {e}")
    return True


def call_fixture_load_function():
    fixture_dir = os.chdir(f"{settings.BASE_DIR}/fixtures")
    items = os.listdir(fixture_dir)
    for item in items:
        print(f"[+] Loading fixture -> {item}")
        call_command('loaddata', item)

    return True


if __name__ == '__main__':
    if env('ENV') == "LOCAL":
        if sys.argv[1] == 'fedup':
            print(f"----------------------------------------------------")
            print(f"===========> It's Okay, I got your back <===========")
            print(f"----------------------------------------------------")

            remove_all_migration_scripts()
            call_migrations_commands()
            call_fixture_load_function()
            call_create_super_function()
        else:
            print("pass 'fedup' as argument in this script. Try -> 'python local_database_cleaner.py fedup'")
    else:
        print("Nah... You can't run this script on staging/prod")
