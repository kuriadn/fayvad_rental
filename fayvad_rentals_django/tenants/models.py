"""
Tenant models for Django
Migrated from FastAPI SQLAlchemy models - preserves all functionality
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import EmailValidator
import uuid

class TenantStatus(models.TextChoices):
    """Tenant status enumeration"""
    PROSPECTIVE = "prospective", "Prospective"
    ACTIVE = "active", "Active"
    FORMER = "former", "Former"
    BLACKLISTED = "blacklisted", "Blacklisted"

class ComplianceStatus(models.TextChoices):
    """Compliance status enumeration"""
    COMPLIANT = "compliant", "Compliant"
    WARNING = "warning", "Warning"
    VIOLATION = "violation", "Violation"


class ComplaintStatus(models.TextChoices):
    """Complaint status enumeration"""
    OPEN = "open", "Open"
    INVESTIGATING = "investigating", "Investigating"
    RESOLVED = "resolved", "Resolved"
    CLOSED = "closed", "Closed"


class ComplaintPriority(models.TextChoices):
    """Complaint priority enumeration"""
    LOW = "low", "Low"
    MEDIUM = "medium", "Medium"
    HIGH = "high", "High"
    URGENT = "urgent", "Urgent"


class ComplaintCategory(models.TextChoices):
    """Complaint category enumeration"""
    NOISE = "noise", "Noise Complaint"
    CLEANLINESS = "cleanliness", "Cleanliness Issue"
    MAINTENANCE = "maintenance", "Maintenance Related"
    NEIGHBOR_DISPUTE = "neighbor_dispute", "Neighbor Dispute"
    FACILITY_ISSUE = "facility_issue", "Facility/Equipment Issue"
    BILLING_DISPUTE = "billing_dispute", "Billing Dispute"
    OTHER = "other", "Other"

class TenantType(models.TextChoices):
    """Tenant type enumeration"""
    STUDENT = "student", "Student"
    PROFESSIONAL = "professional", "Professional"
    OTHER = "other", "Other"

class Tenant(models.Model):
    """
    Tenant model for rental management
    Migrated from FastAPI SQLAlchemy model - all functionality preserved
    """

    # Primary key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Basic information
    name = models.CharField(max_length=200, help_text="Full name of the tenant")
    email = models.EmailField(
        blank=True,
        null=True,
        validators=[EmailValidator()],
        help_text="Email address"
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Phone number"
    )
    id_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        db_index=True,
        help_text="National ID number"
    )

    # Contact information
    emergency_contact_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Emergency contact name"
    )
    emergency_contact_phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Emergency contact phone"
    )

    # Business fields
    tenant_type = models.CharField(
        max_length=20,
        choices=TenantType.choices,
        default=TenantType.OTHER,
        help_text="Type of tenant"
    )
    institution_employer = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Institution or employer name"
    )

    # Status and compliance
    tenant_status = models.CharField(
        max_length=20,
        choices=TenantStatus.choices,
        default=TenantStatus.PROSPECTIVE,
        help_text="Current tenant status"
    )
    compliance_status = models.CharField(
        max_length=20,
        choices=ComplianceStatus.choices,
        default=ComplianceStatus.COMPLIANT,
        help_text="Compliance status"
    )
    compliance_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Notes about compliance status"
    )

    compliance_status_changed = models.DateField(
        null=True,
        blank=True,
        help_text="Date when compliance status last changed"
    )

    violation_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of violations recorded for this tenant"
    )

    # Financial
    account_balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Current account balance"
    )

    # Location association
    current_location = models.ForeignKey(
        'properties.Location',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tenants',
        help_text="Current location/building"
    )

    # User association (if tenant is also a user)
    user = models.OneToOneField(
        'accounts.User',  # Use string reference to avoid circular import
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tenant_profile',
        help_text="Associated user account"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant_status']),
            models.Index(fields=['compliance_status']),
            models.Index(fields=['tenant_type']),
            models.Index(fields=['name']),
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_tenant_status_display()})"

    @property
    def can_assign_room(self) -> bool:
        """Check if tenant can be assigned to a room"""
        return self.tenant_status in [TenantStatus.PROSPECTIVE, TenantStatus.ACTIVE]

    @property
    def current_room(self):
        """Get current room from active rental agreement"""
        active_agreement = self.rental_agreements.filter(status='active').first()
        return active_agreement.room if active_agreement else None

    @property
    def can_transfer_room(self) -> bool:
        """Check if tenant can transfer rooms"""
        return self.tenant_status == TenantStatus.ACTIVE and self.current_room is not None

    @property
    def can_terminate_tenancy(self) -> bool:
        """Check if tenant can terminate tenancy"""
        return self.tenant_status == TenantStatus.ACTIVE

    @property
    def financial_summary(self) -> dict:
        """Get financial summary for tenant"""
        from django.db.models import Sum

        payments_total = self.payments.filter(status='completed').aggregate(
            total=Sum('amount')
        )['total'] or 0

        pending_payments = self.payments.filter(status='pending').aggregate(
            total=Sum('amount')
        )['total'] or 0

        return {
            "account_balance": float(self.account_balance),
            "total_payments": float(payments_total),
            "pending_payments": float(pending_payments),
        }

    @property
    def current_room_number(self) -> str:
        """Get current room number"""
        if hasattr(self, 'current_room') and self.current_room:
            return self.current_room.room_number
        return None

    @property
    def current_location_name(self) -> str:
        """Get current location name"""
        if hasattr(self, 'current_location') and self.current_location:
            return self.current_location.name
        return None


class Complaint(models.Model):
    """
    Complaint model for tenant complaints and grievances
    Normalized separate relation connected to Tenant (BCNF compliance)
    """

    # Primary key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Complaint identification
    complaint_number = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        help_text="Unique complaint reference number"
    )

    # Relations (normalized - single responsibility)
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.PROTECT,  # Prevent deletion if complaints exist
        related_name='complaints',
        help_text="Tenant filing the complaint"
    )

    # Optional relations (avoid over-normalization)
    room = models.ForeignKey(
        'properties.Room',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='complaints',
        help_text="Room related to the complaint (if applicable)"
    )

    assigned_to = models.ForeignKey(
        'accounts.Staff',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_complaints',
        help_text="Staff member assigned to handle the complaint"
    )

    # Complaint details
    category = models.CharField(
        max_length=20,
        choices=ComplaintCategory.choices,
        help_text="Complaint category"
    )

    priority = models.CharField(
        max_length=10,
        choices=ComplaintPriority.choices,
        default=ComplaintPriority.MEDIUM,
        help_text="Complaint priority level"
    )

    subject = models.CharField(
        max_length=200,
        help_text="Brief complaint subject"
    )

    description = models.TextField(
        help_text="Detailed complaint description"
    )

    # Status tracking
    status = models.CharField(
        max_length=15,
        choices=ComplaintStatus.choices,
        default=ComplaintStatus.OPEN,
        help_text="Current complaint status"
    )

    # Resolution
    resolution = models.TextField(
        blank=True,
        null=True,
        help_text="Resolution details and actions taken"
    )

    resolution_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the complaint was resolved"
    )

    # SLA tracking
    priority_changed = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When priority was last changed"
    )

    escalation_deadline = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Deadline for resolution based on priority"
    )

    # Metadata
    is_anonymous = models.BooleanField(
        default=False,
        help_text="Whether the complaint is anonymous"
    )

    contact_preference = models.CharField(
        max_length=20,
        choices=[
            ('email', 'Email'),
            ('phone', 'Phone'),
            ('in_person', 'In Person'),
            ('no_contact', 'No Further Contact'),
        ],
        default='email',
        help_text="Preferred contact method for updates"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Indexes for performance (BCNF compliant)
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['complaint_number']),
            models.Index(fields=['tenant']),
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['category']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.complaint_number or 'Draft'} - {self.subject}"

    def save(self, *args, **kwargs):
        """Auto-generate complaint number if not set"""
        if not self.complaint_number:
            from django.utils import timezone
            timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
            self.complaint_number = f"CMP-{timestamp}-{str(self.id)[:6]}"
        super().save(*args, **kwargs)

    @property
    def is_overdue(self) -> bool:
        """Check if complaint is overdue based on SLA"""
        if self.escalation_deadline and self.status in ['open', 'investigating']:
            from django.utils import timezone
            return timezone.now() > self.escalation_deadline
        return False

    @property
    def days_open(self) -> int:
        """Calculate days since complaint was opened"""
        from django.utils import timezone
        if self.status == 'closed' and self.resolution_date:
            end_date = self.resolution_date
        else:
            end_date = timezone.now()

        delta = end_date - self.created_at
        return delta.days

    @property
    def priority_display(self) -> str:
        """Get human-readable priority"""
        return self.get_priority_display()

    @property
    def status_display(self) -> str:
        """Get human-readable status"""
        return self.get_status_display()

    @property
    def category_display(self) -> str:
        """Get human-readable category"""
        return self.get_category_display()