"""
Custom User model for Django
Migrated from FastAPI user model - preserves all functionality
"""

from django.contrib.auth.models import AbstractUser, BaseUserManager, Group
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

class UserManager(BaseUserManager):
    """Custom manager for User model"""

    def _create_user(self, username, email, password, **extra_fields):
        """Create and save a user with the given username, email, and password."""
        if not username:
            raise ValueError('The Username must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        """Create a regular user"""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        """Create a superuser"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, email, password, **extra_fields)

class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser
    Preserves all fields and functionality from FastAPI user model
    """

    # Additional fields from FastAPI User model
    full_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Full name of the user"
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Phone number"
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Designates whether this user should be treated as active."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Custom manager
    objects = UserManager()

    class Meta:
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['email']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        """Automatically populate full_name from first_name + last_name"""
        if self.first_name or self.last_name:
            self.full_name = f"{self.first_name} {self.last_name}".strip()
        super().save(*args, **kwargs)

    def get_full_name(self):
        """Return the computed full name, fallback to username"""
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.username

    def get_short_name(self):
        """Return the short name, fallback to username"""
        return super().get_short_name() or self.username

    @property
    def profile_complete(self) -> bool:
        """Check if user profile is complete"""
        return bool(
            self.first_name and
            self.last_name and
            self.email
        )

    @property
    def account_status(self) -> str:
        """Get account status"""
        if not self.is_active:
            return "inactive"
        elif self.is_superuser:
            return "admin"
        elif hasattr(self, 'staff_profile'):
            return "staff"
        else:
            return "user"


class Staff(models.Model):
    """
    Staff model for rental management system
    Handles managers, cleaners, caretakers, and other staff roles
    """

    class StaffRole(models.TextChoices):
        MANAGER = 'manager', 'Manager'
        CLEANER = 'cleaner', 'Cleaner'
        CARETAKER = 'caretaker', 'Caretaker'
        MAINTENANCE = 'maintenance', 'Maintenance Technician'
        SECURITY = 'security', 'Security Guard'

    # User association
    user = models.OneToOneField(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='staff_profile',
        help_text="Associated user account"
    )

    # Staff details
    role = models.CharField(
        max_length=20,
        choices=StaffRole.choices,
        default=StaffRole.CARETAKER,
        help_text="Staff role/position"
    )

    employee_id = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        help_text="Unique employee identification number"
    )

    department = models.CharField(
        max_length=100,
        blank=True,
        help_text="Department or section"
    )

    hire_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date staff member was hired"
    )

    is_active_staff = models.BooleanField(
        default=True,
        help_text="Whether this staff member is currently active"
    )

    # Contact info (can be different from user account)
    emergency_contact_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Emergency contact person"
    )

    emergency_contact_phone = models.CharField(
        max_length=20,
        blank=True,
        help_text="Emergency contact phone number"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['user__full_name']
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['employee_id']),
            models.Index(fields=['is_active_staff']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_role_display()}"

    @property
    def full_name(self):
        """Get staff member's full name"""
        return self.user.get_full_name()

    @property
    def email(self):
        """Get staff member's email"""
        return self.user.email

    @property
    def phone(self):
        """Get staff member's phone"""
        return self.user.phone or ""

    def can_manage_locations(self) -> bool:
        """Check if staff member can manage locations"""
        return self.role in [self.StaffRole.MANAGER, self.StaffRole.CARETAKER]

    def can_handle_maintenance(self) -> bool:
        """Check if staff member can handle maintenance tasks"""
        return self.role in [self.StaffRole.MAINTENANCE, self.StaffRole.CARETAKER]

    def can_clean_rooms(self) -> bool:
        """Check if staff member can clean rooms"""
        return self.role in [self.StaffRole.CLEANER, self.StaffRole.CARETAKER]


# ===== SIGNALS =====

@receiver(post_save, sender=User)
def ensure_superuser_in_manager_group(sender, instance, created, **kwargs):
    """
    Ensure that superusers are always in the Manager group
    This provides consistent permissions across the application
    """
    if instance.is_superuser:
        # Get or create Manager group
        manager_group, _ = Group.objects.get_or_create(name='Manager')
        # Add superuser to Manager group if not already in it
        if not instance.groups.filter(name='Manager').exists():
            instance.groups.add(manager_group)