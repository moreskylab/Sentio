from django.core.management.base import BaseCommand
# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
# Import your models here
from recommendations.models import CustomUser

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with initial data if it does not exist'

    def handle(self, *args, **kwargs):
        # Example 1: Create a superuser if none exists
        if not CustomUser.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser('admin@mail.com', 'Pp@$$w0rd.')
            self.stdout.write(self.style.SUCCESS('Successfully created superuser.'))
        else:
            self.stdout.write(self.style.WARNING('Superuser already exists. Skipping.'))

        # Example 2: Seed other data if empty
        # if not ExampleModel.objects.exists():
        #     ExampleModel.objects.create(name="Initial Data")
        #     self.stdout.write(self.style.SUCCESS('Successfully seeded ExampleModel.'))
        # else:
        #     self.stdout.write(self.style.WARNING('ExampleModel already has data. Skipping.'))