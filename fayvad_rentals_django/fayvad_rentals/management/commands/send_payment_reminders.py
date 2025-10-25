"""
Management command to send automated payment reminders for overdue rent
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
import logging

from tenants.models import Tenant
from rentals.models import RentalAgreement
from workflows.services.notifications import NotificationService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Send automated payment reminders for overdue rent'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what reminders would be sent without actually sending them',
        )
        parser.add_argument(
            '--days-overdue',
            type=int,
            default=7,
            help='Number of days past due date to consider (default: 7)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        days_overdue = options['days_overdue']

        if dry_run:
            self.stdout.write('DRY RUN MODE - No notifications will be sent')

        cutoff_date = timezone.now().date() - timedelta(days=days_overdue)
        reminders_sent = 0

        # Find active tenants with overdue rent
        overdue_tenants = []

        # Get all active rental agreements
        active_agreements = RentalAgreement.objects.filter(
            status='active',
            end_date__gte=timezone.now().date()  # Not yet ended
        ).select_related('tenant')

        for agreement in active_agreements:
            # Check if rent is overdue for this agreement
            if self._is_rent_overdue(agreement, cutoff_date):
                overdue_tenants.append(agreement)

        # Send reminders
        for agreement in overdue_tenants:
            if dry_run:
                self.stdout.write(
                    f'WOULD REMIND: {agreement.tenant.name} - '
                    f'Amount: KES {agreement.monthly_rent}, '
                    f'Days overdue: {self._get_days_overdue(agreement)}'
                )
            else:
                success = self._send_payment_reminder(agreement)
                if success:
                    reminders_sent += 1
                    self.stdout.write(
                        f'SENT REMINDER: {agreement.tenant.name} - '
                        f'KES {agreement.monthly_rent}'
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'FAILED TO REMIND: {agreement.tenant.name}')
                    )

        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully sent {reminders_sent} payment reminders')
            )

    def _is_rent_overdue(self, agreement, cutoff_date):
        """Check if rent is overdue for this agreement"""
        try:
            # Get the last payment date for this tenant
            from payments.models import Payment

            last_payment = Payment.objects.filter(
                tenant=agreement.tenant,
                status='completed'
            ).order_by('-payment_date').first()

            if last_payment:
                # Calculate next due date (simplified - assumes monthly payments)
                next_due = last_payment.payment_date + timedelta(days=30)
                return next_due.date() <= cutoff_date
            else:
                # No payments found, assume first payment is overdue
                # Use agreement start date + 30 days as first due date
                first_due = agreement.start_date + timedelta(days=30)
                return first_due <= cutoff_date

        except Exception as e:
            logger.error(f"Error checking overdue status for agreement {agreement.id}: {e}")
            return False

    def _get_days_overdue(self, agreement):
        """Calculate how many days rent is overdue"""
        try:
            from payments.models import Payment

            last_payment = Payment.objects.filter(
                tenant=agreement.tenant,
                status='completed'
            ).order_by('-payment_date').first()

            if last_payment:
                next_due = last_payment.payment_date + timedelta(days=30)
                days_overdue = (timezone.now().date() - next_due.date()).days
                return max(0, days_overdue)
            else:
                first_due = agreement.start_date + timedelta(days=30)
                days_overdue = (timezone.now().date() - first_due).days
                return max(0, days_overdue)

        except Exception as e:
            logger.error(f"Error calculating days overdue for agreement {agreement.id}: {e}")
            return 0

    def _send_payment_reminder(self, agreement):
        """Send payment reminder notification"""
        try:
            # Create notification for the tenant
            from workflows.services.notifications import WorkflowNotification

            # Calculate overdue amount and days
            days_overdue = self._get_days_overdue(agreement)
            overdue_amount = agreement.monthly_rent

            title = f'Rent Payment Overdue - {days_overdue} days past due'
            message = (
                f'Dear {agreement.tenant.name},\n\n'
                f'Your rent payment of KES {overdue_amount:,} is {days_overdue} days overdue.\n'
                f'Please make payment as soon as possible to avoid late fees.\n\n'
                f'Room: {agreement.room.room_number if agreement.room else "N/A"}\n'
                f'Monthly Rent: KES {agreement.monthly_rent:,}\n\n'
                f'You can make payment through M-Pesa or bank transfer.\n'
                f'Contact us if you need assistance.'
            )

            notification = WorkflowNotification.objects.create(
                recipient=agreement.tenant.user,
                notification_type='in_app',
                priority='high',
                title=title,
                message=message,
                instance_type='RentalAgreement',
                instance_id=str(agreement.id),
                event_type='payment_reminder',
                event_data={
                    'days_overdue': days_overdue,
                    'overdue_amount': overdue_amount,
                    'agreement_id': agreement.id
                }
            )

            # Mark as sent (in-app notifications are immediately "sent")
            notification.mark_as_sent()

            # Log the reminder
            from workflows.services.audit import AuditLogService
            AuditLogService.log_event(
                instance_type='RentalAgreement',
                instance_id=str(agreement.id),
                event_type='notification',
                event_name='payment_reminder_sent',
                user=None,  # System action
                metadata={
                    'days_overdue': days_overdue,
                    'overdue_amount': overdue_amount,
                    'reminder_type': 'automated'
                },
                notes=f'Automated payment reminder sent for {days_overdue} days overdue'
            )

            return True

        except Exception as e:
            logger.error(f"Failed to send payment reminder for agreement {agreement.id}: {e}")
            return False
