"""
Property management models
Locations and Rooms for rental management
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
import uuid

class Location(models.Model):
    """
    Location/Property model for rental management
    Buildings, complexes, or property locations
    """

    # Primary key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Basic information
    name = models.CharField(
        max_length=200,
        help_text="Location name (e.g., 'Building A', 'Campus Complex')"
    )
    code = models.CharField(
        max_length=10,
        unique=True,
        validators=[RegexValidator(
            regex=r'^[A-Z0-9]+$',
            message='Code must be uppercase letters and numbers only'
        )],
        help_text="Unique location code (e.g., 'BLDA', 'CAMPUS')"
    )

    # Address information
    address = models.TextField(
        blank=True,
        null=True,
        help_text="Full address of the location"
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="City where location is situated"
    )

    # Management
    manager = models.ForeignKey(
        'accounts.Staff',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_locations',
        help_text="Location manager/caretaker"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this location is active"
    )

    # Setup status
    setup_complete = models.BooleanField(
        default=False,
        help_text="Whether location setup is complete"
    )
    setup_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When setup was completed"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['is_active']),
            models.Index(fields=['setup_complete']),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"

    @property
    def room_count(self) -> int:
        """Get total number of rooms"""
        return self.rooms.count()

    @property
    def occupied_room_count(self) -> int:
        """Get number of occupied rooms"""
        return self.rooms.filter(status='occupied').count()

    @property
    def available_room_count(self) -> int:
        """Get number of available rooms"""
        return self.rooms.filter(status='available').count()

    @property
    def tenant_count(self) -> int:
        """Get number of tenants in this location"""
        return self.rooms.filter(rental_agreements__status='active').distinct().count()

    @property
    def occupancy_rate(self) -> float:
        """Calculate occupancy rate percentage"""
        if self.room_count == 0:
            return 0.0
        return round((self.occupied_room_count / self.room_count) * 100, 2)

    @property
    def monthly_revenue(self) -> float:
        """Calculate monthly revenue from active rental agreements"""
        from rentals.models import RentalAgreement
        revenue = 0.0
        for agreement in RentalAgreement.objects.filter(
            room__location=self, status='active'
        ).select_related('room'):
            revenue += float(agreement.rent_amount)
        return revenue

    def complete_setup(self):
        """Mark location setup as complete"""
        from django.utils import timezone
        self.setup_complete = True
        self.setup_date = timezone.now()
        self.save()

    def clean(self):
        """Validate model data"""
        if self.code:
            self.code = self.code.upper()


class RoomType(models.TextChoices):
    """Room type choices"""
    SINGLE = "single", "Single Room"
    DOUBLE = "double", "Double Room"
    STUDIO = "studio", "Studio"
    ONE_BEDROOM = "one_bedroom", "1 Bedroom"
    TWO_BEDROOM = "two_bedroom", "2 Bedroom"
    SHARED = "shared", "Shared Room"


class RoomStatus(models.TextChoices):
    """Room status choices"""
    AVAILABLE = "available", "Available"
    OCCUPIED = "occupied", "Occupied"
    MAINTENANCE = "maintenance", "Under Maintenance"
    RESERVED = "reserved", "Reserved"


class Room(models.Model):
    """
    Room model for rental management
    Individual rental units within locations
    """

    # Primary key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Basic information
    room_number = models.CharField(
        max_length=20,
        help_text="Room number or identifier"
    )
    room_type = models.CharField(
        max_length=20,
        choices=RoomType.choices,
        default=RoomType.SINGLE,
        help_text="Type of room"
    )

    # Location and position
    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name='rooms',
        help_text="Location/building this room belongs to"
    )
    floor = models.IntegerField(
        null=True,
        blank=True,
        help_text="Floor number"
    )
    capacity = models.IntegerField(
        default=1,
        help_text="Maximum occupancy"
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=RoomStatus.choices,
        default=RoomStatus.AVAILABLE,
        help_text="Current room status"
    )

    # Description
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Room description and amenities"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['location', 'room_number']
        unique_together = ['location', 'room_number']
        indexes = [
            models.Index(fields=['location', 'status']),
            models.Index(fields=['status']),
            models.Index(fields=['room_type']),
        ]

    def __str__(self):
        return f"{self.location.code}-{self.room_number}"

    @property
    def is_available(self) -> bool:
        """Check if room is available for rent"""
        return self.status == RoomStatus.AVAILABLE

    @property
    def is_occupied(self) -> bool:
        """Check if room is currently occupied"""
        return self.status == RoomStatus.OCCUPIED

    @property
    def is_under_maintenance(self) -> bool:
        """Check if room is under maintenance"""
        return self.status == RoomStatus.MAINTENANCE

    @property
    def full_room_identifier(self) -> str:
        """Get full room identifier with location"""
        return f"{self.location.code}-{self.room_number}"

    @property
    def monthly_revenue(self) -> float:
        """Get monthly revenue from active rental agreement"""
        active_agreement = self.rental_agreements.filter(status='active').first()
        return float(active_agreement.rent_amount) if active_agreement else 0.0


    def mark_for_maintenance(self):
        """Mark room for maintenance"""
        self.status = RoomStatus.MAINTENANCE
        self.save()

    def mark_available(self):
        """Mark room as available"""
        if self.status == RoomStatus.MAINTENANCE:
            self.status = RoomStatus.AVAILABLE
            self.save()

    def clean(self):
        """Validate model data"""
        if self.capacity < 1:
            raise ValueError("Room capacity must be at least 1")
        if self.capacity > 10:
            raise ValueError("Room capacity cannot exceed 10")
