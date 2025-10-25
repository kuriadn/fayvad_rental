"""
Maintenance request management models
Property repair and maintenance tracking
"""

from django.db import models
from django.utils import timezone
import uuid

class Priority(models.TextChoices):
    """Maintenance priority choices"""
    LOW = "low", "Low"
    MEDIUM = "medium", "Medium"
    HIGH = "high", "High"
    URGENT = "urgent", "Urgent"


class MaintenanceStatus(models.TextChoices):
    """Maintenance status choices"""
    PENDING = "pending", "Pending"
    IN_PROGRESS = "in_progress", "In Progress"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"


class MaintenanceRequest(models.Model):
    """
    Maintenance Request model for property repairs and maintenance
    """

    # Primary key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Request identification
    request_number = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        help_text="Unique maintenance request reference number"
    )

    # Request details
    title = models.CharField(
        max_length=200,
        help_text="Brief title describing the maintenance issue"
    )
    description = models.TextField(
        help_text="Detailed description of the maintenance issue"
    )

    # Attachments - stored as comma-separated URLs
    photos = models.TextField(
        blank=True,
        null=True,
        help_text="Comma-separated list of photo URLs attached to the request"
    )
    documents = models.TextField(
        blank=True,
        null=True,
        help_text="Comma-separated list of document URLs attached to the request"
    )

    # Related entities
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.PROTECT,  # Changed from CASCADE to preserve maintenance history
        related_name='maintenance_requests',
        help_text="Tenant who reported the issue"
    )
    room = models.ForeignKey(
        'properties.Room',
        on_delete=models.PROTECT,  # Changed from CASCADE to preserve maintenance history
        related_name='maintenance_requests',
        help_text="Room where maintenance is needed"
    )
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,  # Changed from CASCADE to preserve maintenance history
        related_name='maintenance_requests',
        help_text="User who created the request"
    )

    # Priority and status
    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM,
        help_text="Priority level of the maintenance request"
    )
    status = models.CharField(
        max_length=20,
        choices=MaintenanceStatus.choices,
        default=MaintenanceStatus.PENDING,
        help_text="Current status of the maintenance request"
    )

    # Dates
    requested_date = models.DateTimeField(
        auto_now_add=True,
        help_text="When the maintenance was requested"
    )
    scheduled_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Scheduled date for maintenance work"
    )
    completed_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date when maintenance was completed"
    )

    # Cost tracking
    estimated_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Estimated cost of maintenance work"
    )
    actual_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Actual cost incurred for maintenance"
    )

    # Assignment
    assigned_to = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Technician or staff assigned to the request"
    )
    assigned_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the request was assigned"
    )

    # Resolution
    resolution_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Notes about how the issue was resolved"
    )
    resolution_photos = models.JSONField(
        null=True,
        blank=True,
        help_text="JSON array of photo URLs showing before/after"
    )

    # Follow-up
    follow_up_required = models.BooleanField(
        default=False,
        help_text="Whether follow-up is required"
    )
    follow_up_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date for follow-up check"
    )
    follow_up_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Notes from follow-up visit"
    )

    # Tenant Satisfaction Feedback
    tenant_satisfaction_rating = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        choices=[(1, 'Very Dissatisfied'), (2, 'Dissatisfied'), (3, 'Neutral'), (4, 'Satisfied'), (5, 'Very Satisfied')],
        help_text="Tenant's satisfaction rating (1-5 scale)"
    )
    tenant_feedback = models.TextField(
        blank=True,
        null=True,
        help_text="Tenant's feedback on the maintenance resolution"
    )
    feedback_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When tenant provided feedback"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['request_number']),
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['requested_date']),
            models.Index(fields=['scheduled_date']),
            models.Index(fields=['completed_date']),
            models.Index(fields=['tenant']),
            models.Index(fields=['room']),
            models.Index(fields=['created_by']),
        ]

    def __str__(self):
        return f"Maintenance {self.request_number or self.id} - {self.title}"

    @property
    def is_pending(self) -> bool:
        """Check if request is pending"""
        return self.status == MaintenanceStatus.PENDING

    @property
    def is_in_progress(self) -> bool:
        """Check if request is in progress"""
        return self.status == MaintenanceStatus.IN_PROGRESS

    @property
    def is_completed(self) -> bool:
        """Check if request is completed"""
        return self.status == MaintenanceStatus.COMPLETED

    @property
    def days_pending(self) -> int:
        """Calculate days request has been pending"""
        if self.status != MaintenanceStatus.PENDING:
            return 0
        from django.utils import timezone
        return (timezone.now() - self.requested_date).days

    @property
    def days_to_completion(self) -> int:
        """Calculate days taken to complete"""
        if not self.completed_date:
            return 0
        return (self.completed_date - self.requested_date).days

    @property
    def cost_variance(self) -> float:
        """Calculate cost variance from estimate"""
        if not self.estimated_cost or not self.actual_cost:
            return 0.0
        return float(self.actual_cost - self.estimated_cost)

    @property
    def is_overdue(self) -> bool:
        """Check if maintenance is overdue"""
        if self.status == MaintenanceStatus.COMPLETED:
            return False

        # Urgent requests should be completed within 1 day
        if self.priority == Priority.URGENT:
            return self.days_pending > 1

        # High priority within 3 days
        elif self.priority == Priority.HIGH:
            return self.days_pending > 3

        # Medium priority within 7 days
        elif self.priority == Priority.MEDIUM:
            return self.days_pending > 7

        # Low priority within 14 days
        else:
            return self.days_pending > 14

    @property
    def can_be_assigned(self) -> bool:
        """Check if request can be assigned"""
        return self.status in [MaintenanceStatus.PENDING, MaintenanceStatus.IN_PROGRESS]

    @property
    def can_be_completed(self) -> bool:
        """Check if request can be completed"""
        return self.status == MaintenanceStatus.IN_PROGRESS

    @property
    def can_be_cancelled(self) -> bool:
        """Check if request can be cancelled"""
        return self.status in [MaintenanceStatus.PENDING, MaintenanceStatus.IN_PROGRESS]

    @property
    def photo_urls(self):
        """Get photo URLs as a list"""
        if self.photos:
            return [url.strip() for url in self.photos.split(',') if url.strip()]
        return []

    @property
    def document_urls(self):
        """Get document URLs as a list"""
        if self.documents:
            return [url.strip() for url in self.documents.split(',') if url.strip()]
        return []

    def assign_technician(self, technician_name: str):
        """Assign technician to request"""
        self.assigned_to = technician_name
        self.assigned_date = timezone.now()
        if self.status == MaintenanceStatus.PENDING:
            self.status = MaintenanceStatus.IN_PROGRESS
        self.save()

    def complete_request(self, resolution_notes=None, actual_cost=None):
        """Mark request as completed"""
        self.status = MaintenanceStatus.COMPLETED
        self.completed_date = timezone.now()

        if resolution_notes:
            self.resolution_notes = resolution_notes

        if actual_cost is not None:
            self.actual_cost = actual_cost

        self.save()

    def schedule_maintenance(self, scheduled_date):
        """Schedule maintenance"""
        self.scheduled_date = scheduled_date
        self.save()

    def cancel_request(self):
        """Cancel maintenance request"""
        self.status = MaintenanceStatus.CANCELLED
        self.save()

    def generate_request_number(self) -> str:
        """Generate unique request number"""
        if not self.request_number:
            from django.utils import timezone
            timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
            self.request_number = f"MNT-{timestamp}-{str(self.id)[:8]}"
            self.save()
        return self.request_number

    def clean(self):
        """Validate model data"""
        if not self.title or not self.title.strip():
            raise ValueError("Title cannot be empty")
        if not self.description or not self.description.strip():
            raise ValueError("Description cannot be empty")

    def save(self, *args, **kwargs):
        """Override save to generate request number"""
        super().save(*args, **kwargs)
        if not self.request_number:
            self.generate_request_number()
