"""
Rental agreement management models
Contracts between tenants and rental properties
"""

from django.db import models
import uuid

class AgreementStatus(models.TextChoices):
    """Rental agreement status choices"""
    DRAFT = "draft", "Draft"
    ACTIVE = "active", "Active"
    EXPIRED = "expired", "Expired"
    TERMINATED = "terminated", "Terminated"


class RentalAgreement(models.Model):
    """
    Rental Agreement model for tenancy contracts
    """

    # Primary key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Agreement identification
    agreement_number = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        help_text="Unique agreement reference number"
    )

    # Parties
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.PROTECT,  # Changed from CASCADE to prevent accidental deletion
        related_name='rental_agreements',
        help_text="Tenant party to the agreement"
    )
    room = models.ForeignKey(
        'properties.Room',
        on_delete=models.PROTECT,  # Changed from CASCADE to prevent accidental deletion
        related_name='rental_agreements',
        help_text="Room being rented"
    )

    # Terms
    start_date = models.DateField(
        help_text="Agreement start date"
    )
    end_date = models.DateField(
        help_text="Agreement end date"
    )
    rent_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Monthly rent amount"
    )
    deposit_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Security deposit amount"
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=AgreementStatus.choices,
        default=AgreementStatus.DRAFT,
        help_text="Current agreement status"
    )

    # Notice and termination
    notice_given_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date when notice was given"
    )
    notice_period_days = models.PositiveIntegerField(
        default=30,
        help_text="Notice period in days"
    )

    # Additional terms
    special_terms = models.TextField(
        blank=True,
        null=True,
        help_text="Special terms and conditions"
    )
    security_deposit_returned = models.BooleanField(
        default=False,
        help_text="Whether security deposit has been returned"
    )
    security_deposit_return_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date when security deposit was returned"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['agreement_number']),
            models.Index(fields=['status']),
            models.Index(fields=['start_date']),
            models.Index(fields=['end_date']),
            models.Index(fields=['tenant']),
            models.Index(fields=['room']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_date__gt=models.F('start_date')),
                name='end_date_after_start_date'
            ),
            models.CheckConstraint(
                check=models.Q(rent_amount__gt=0),
                name='rent_amount_positive'
            ),
            models.CheckConstraint(
                check=models.Q(deposit_amount__gte=0),
                name='deposit_amount_non_negative'
            ),
        ]

    def __str__(self):
        return f"Agreement {self.agreement_number or self.id} - {self.tenant.name}"

    @property
    def duration_days(self) -> int:
        """Calculate agreement duration in days"""
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days
        return 0

    @property
    def duration_months(self) -> float:
        """Calculate agreement duration in months"""
        return self.duration_days / 30.44  # Average month length

    @property
    def is_active(self) -> bool:
        """Check if agreement is currently active"""
        from datetime import date
        today = date.today()
        return (
            self.status == AgreementStatus.ACTIVE and
            self.start_date <= today <= self.end_date
        )

    @property
    def is_expired(self) -> bool:
        """Check if agreement has expired"""
        from datetime import date
        today = date.today()
        return self.end_date < today and self.status != AgreementStatus.TERMINATED

    @property
    def days_until_expiry(self) -> int:
        """Calculate days until agreement expires"""
        if not self.end_date:
            return 0
        from datetime import date
        today = date.today()
        return (self.end_date - today).days

    @property
    def outstanding_balance(self) -> float:
        """Calculate outstanding balance"""
        total_paid = sum(
            payment.amount for payment in self.payments.filter(status='completed')
        )
        total_owed = (self.rent_amount * self.duration_months) + self.deposit_amount
        return float(total_owed - total_paid)

    @property
    def monthly_rent_due(self) -> float:
        """Get monthly rent amount"""
        return float(self.rent_amount)

    @property
    def total_contract_value(self) -> float:
        """Calculate total contract value"""
        return float((self.rent_amount * self.duration_months) + self.deposit_amount)

    @property
    def can_be_terminated(self) -> bool:
        """Check if agreement can be terminated"""
        return self.status in [AgreementStatus.DRAFT, AgreementStatus.ACTIVE]

    @property
    def is_notice_period_active(self) -> bool:
        """Check if notice period is currently active"""
        if not self.notice_given_date:
            return False
        from datetime import date, timedelta
        today = date.today()
        notice_end_date = self.notice_given_date + timedelta(days=self.notice_period_days)
        return self.notice_given_date <= today <= notice_end_date

    def activate_agreement(self):
        """Activate the rental agreement"""
        if self.status == AgreementStatus.DRAFT:
            self.status = AgreementStatus.ACTIVE
            # Update room status to occupied
            if self.room:
                from properties.models import RoomStatus
                self.room.status = RoomStatus.OCCUPIED
                self.room.save()
            self.save()

    def terminate_agreement(self, termination_date=None):
        """Terminate the rental agreement"""
        from datetime import date
        self.status = AgreementStatus.TERMINATED
        if termination_date:
            self.end_date = termination_date
        else:
            self.end_date = date.today()

        # Check if room should be made available
        if self.room:
            # Only make room available if there are no other active agreements for this room
            other_active_agreements = RentalAgreement.objects.filter(
                room=self.room,
                status__in=[AgreementStatus.ACTIVE, AgreementStatus.DRAFT]
            ).exclude(pk=self.pk)

            if not other_active_agreements.exists():
                from properties.models import RoomStatus
                self.room.status = RoomStatus.AVAILABLE
                self.room.save()

        self.save()

    def give_notice(self, notice_date=None):
        """Give notice for termination"""
        from datetime import date
        if notice_date is None:
            notice_date = date.today()
        self.notice_given_date = notice_date
        self.save()

    def validate_dates(self) -> bool:
        """Validate agreement dates"""
        if not self.start_date or not self.end_date:
            return False
        return self.start_date < self.end_date

    def validate_amounts(self) -> bool:
        """Validate agreement amounts"""
        return self.rent_amount > 0 and self.deposit_amount >= 0

    def generate_agreement_number(self) -> str:
        """Generate unique agreement number"""
        if not self.agreement_number:
            from django.utils import timezone
            timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
            self.agreement_number = f"RA-{timestamp}-{str(self.id)[:8]}"
            self.save()
        return self.agreement_number

    def clean(self):
        """Validate model data"""
        if not self.validate_dates():
            raise ValueError("End date must be after start date")
        if not self.validate_amounts():
            raise ValueError("Invalid amounts: rent must be positive, deposit must be non-negative")

    def save(self, *args, **kwargs):
        """Override save to generate agreement number"""
        super().save(*args, **kwargs)
        if not self.agreement_number:
            self.generate_agreement_number()
