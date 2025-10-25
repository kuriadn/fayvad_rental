"""
Payment management models
Rent collection, deposits, and payment tracking
"""

from django.db import models
import uuid

class PaymentMethod(models.TextChoices):
    """Payment method choices"""
    CASH = "cash", "Cash"
    MPESA = "mpesa", "M-Pesa"
    BANK_TRANSFER = "bank_transfer", "Bank Transfer"
    CHEQUE = "cheque", "Cheque"
    CARD = "card", "Card"
    OTHER = "other", "Other"


class PaymentStatus(models.TextChoices):
    """Payment status choices"""
    PENDING = "pending", "Pending"
    COMPLETED = "completed", "Completed"
    FAILED = "failed", "Failed"
    REFUNDED = "refunded", "Refunded"
    CANCELLED = "cancelled", "Cancelled"


class Payment(models.Model):
    """
    Payment model for rent and other charges
    """

    # Primary key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Payment identification
    payment_number = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        help_text="Unique payment reference number"
    )

    # Amount and method
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Payment amount"
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.MPESA,
        help_text="Payment method used"
    )

    # Reference
    reference_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="External reference (e.g., M-Pesa transaction ID)"
    )

    # Related entities
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments',
        help_text="Tenant making the payment"
    )
    rental_agreement = models.ForeignKey(
        'rentals.RentalAgreement',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments',
        help_text="Associated rental agreement"
    )
    room = models.ForeignKey(
        'properties.Room',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments',
        help_text="Room payment is for"
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        help_text="Current payment status"
    )

    # Dates
    payment_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date payment was made"
    )
    processed_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When payment was processed"
    )

    # Notes and description
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional payment notes"
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Payment description"
    )

    # Processing details
    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="External transaction identifier"
    )
    processor_response = models.TextField(
        blank=True,
        null=True,
        help_text="Response from payment processor"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['payment_number']),
            models.Index(fields=['reference_number']),
            models.Index(fields=['transaction_id']),
            models.Index(fields=['status']),
            models.Index(fields=['payment_date']),
            models.Index(fields=['tenant']),
            models.Index(fields=['rental_agreement']),
        ]

    def __str__(self):
        return f"Payment {self.payment_number or self.id} - {self.amount}"

    @property
    def is_completed(self) -> bool:
        """Check if payment is completed"""
        return self.status == PaymentStatus.COMPLETED

    @property
    def is_pending(self) -> bool:
        """Check if payment is pending"""
        return self.status == PaymentStatus.PENDING

    @property
    def is_failed(self) -> bool:
        """Check if payment failed"""
        return self.status == PaymentStatus.FAILED

    @property
    def is_refundable(self) -> bool:
        """Check if payment can be refunded"""
        return self.status == PaymentStatus.COMPLETED

    @property
    def days_overdue(self) -> int:
        """Calculate days payment is overdue"""
        if not self.payment_date:
            return 0
        from datetime import date
        today = date.today()
        if self.payment_date >= today:
            return 0
        return (today - self.payment_date).days

    @property
    def is_overdue(self) -> bool:
        """Check if payment is overdue"""
        return self.days_overdue > 0

    def complete_payment(self, transaction_id=None):
        """Mark payment as completed"""
        from django.utils import timezone
        self.status = PaymentStatus.COMPLETED
        self.processed_date = timezone.now()
        if transaction_id:
            self.transaction_id = transaction_id
        self.save()

    def fail_payment(self, reason=None):
        """Mark payment as failed"""
        self.status = PaymentStatus.FAILED
        if reason:
            self.processor_response = reason
        self.save()

    def refund_payment(self, refund_amount=None):
        """Process payment refund"""
        if self.status != PaymentStatus.COMPLETED:
            raise ValueError("Can only refund completed payments")

        self.status = PaymentStatus.REFUNDED
        if refund_amount and refund_amount != self.amount:
            self.notes = f"Partial refund: {refund_amount} of {self.amount}"
        self.save()

    def generate_payment_number(self) -> str:
        """Generate unique payment number"""
        if not self.payment_number:
            from django.utils import timezone
            timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
            self.payment_number = f"PAY-{timestamp}-{str(self.id)[:8]}"
            self.save()
        return self.payment_number

    def clean(self):
        """Validate model data"""
        if self.amount <= 0:
            raise ValueError("Payment amount must be greater than zero")

    def save(self, *args, **kwargs):
        """Override save to generate payment number"""
        super().save(*args, **kwargs)
        if not self.payment_number:
            self.generate_payment_number()
