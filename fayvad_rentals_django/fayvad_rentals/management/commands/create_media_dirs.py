"""
Management command to create media directories for file uploads.
This ensures that all necessary directories exist before file uploads.
"""

from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Create media directories for file uploads'

    def handle(self, *args, **options):
        """Create all necessary media directories."""
        self.stdout.write('Creating media directories...')

        # Define all required directories
        directories = [
            'documents',  # For general document uploads
            'maintenance',  # Base maintenance directory
            os.path.join('maintenance', 'photos'),  # Maintenance photos
            os.path.join('maintenance', 'documents'),  # Maintenance documents
            'avatars',  # User avatars
            'property_images',  # Property images
        ]

        created_count = 0

        for directory in directories:
            try:
                if not default_storage.exists(directory):
                    default_storage.makedirs(directory)
                    created_count += 1
                    self.stdout.write(f'  ✓ Created: {directory}')
                else:
                    self.stdout.write(f'  - Exists: {directory}')
            except Exception as e:
                self.stderr.write(f'  ✗ Failed to create {directory}: {e}')

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} media directories.'
            )
        )
