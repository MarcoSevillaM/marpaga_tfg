from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone

# Script que elimina los usuarios que tienen la cuenta inactiva durantes mas de un dia
class Command(BaseCommand):
    help = 'Delete inactive users older than 1 day'

    def handle(self, *args, **options):
        users = User.objects.filter(is_active=False)
        for user in users:
            if timezone.now() - user.date_joined > timedelta(days=1):
                user.delete()
                self.stdout.write(self.style.SUCCESS(f'User {user.username} deleted'))
            else:
                self.stdout.write(self.style.SUCCESS(f'User {user.username} is not older than 1 day'))
