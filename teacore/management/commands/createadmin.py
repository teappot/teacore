from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from teacore.models import Lang

class Command(BaseCommand):
    help = "Create base configuration."

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username for the superuser')
        parser.add_argument('password', type=str, help='Password for the superuser')
        
    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("Create admin ..."))

        username = options.get('username')
        password = options.get('password')
        # Create superuser
        superuser = User.objects.create_superuser(
            username=username,
            email=username,
            password=password,
        )
        superuser.save()
        self.stdout.write(self.style.SUCCESS(f"Admin (superuser) created successfully. ({username} » {password})"))


