"""
Management command to sync superuser group memberships
Ensures all superusers are in the Manager group
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group


class Command(BaseCommand):
    help = 'Sync superuser group memberships - ensures all superusers are in Manager group'

    def handle(self, *args, **options):
        User = get_user_model()

        # Get or create Manager group
        manager_group, created = Group.objects.get_or_create(name='Manager')
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created Manager group'))

        # Get all superusers
        superusers = User.objects.filter(is_superuser=True)
        synced_count = 0

        for user in superusers:
            if not user.groups.filter(name='Manager').exists():
                user.groups.add(manager_group)
                self.stdout.write(f'Added {user.username} to Manager group')
                synced_count += 1
            else:
                self.stdout.write(self.style.SUCCESS(f'{user.username} already in Manager group'))

        if synced_count > 0:
            self.stdout.write(self.style.SUCCESS(f'Synced {synced_count} superusers to Manager group'))
        else:
            self.stdout.write(self.style.SUCCESS('All superusers are already in Manager group'))
