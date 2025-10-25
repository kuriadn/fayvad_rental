"""
Management command to process SLA escalations for overdue maintenance requests
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
import logging

from maintenance.models import MaintenanceRequest
from workflows.services.notifications import NotificationService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Process SLA escalations for overdue maintenance requests'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be escalated without actually doing it',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        if dry_run:
            self.stdout.write('DRY RUN MODE - No changes will be made')

        # SLA thresholds (in hours)
        SLA_THRESHOLDS = {
            'urgent': 2,    # Escalate urgent priority after 2 hours
            'high': 24,     # Escalate high priority after 24 hours
            'medium': 72,   # Escalate medium priority after 3 days
            'low': 168,     # Escalate low priority after 7 days
        }

        now = timezone.now()
        escalated_count = 0

        for priority, hours in SLA_THRESHOLDS.items():
            # Find requests that are overdue for their priority level
            sla_deadline = now - timedelta(hours=hours)

            overdue_requests = MaintenanceRequest.objects.filter(
                Q(status__in=['pending', 'assigned', 'in_progress']) &
                Q(priority=priority) &
                Q(created_at__lt=sla_deadline)
            )

            for request in overdue_requests:
                if dry_run:
                    self.stdout.write(
                        f'WOULD ESCALATE: {request.request_number} - {request.title} '
                        f'(Priority: {priority}, Age: {(now - request.created_at).days} days)'
                    )
                else:
                    # Escalate the request
                    success = self._escalate_request(request)
                    if success:
                        escalated_count += 1
                        self.stdout.write(
                            f'ESCALATED: {request.request_number} - {request.title}'
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(f'FAILED TO ESCALATE: {request.request_number}')
                        )

        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully escalated {escalated_count} maintenance requests')
            )

    def _escalate_request(self, request):
        """Escalate a maintenance request"""
        try:
            # Determine new priority (escalate one level up)
            priority_escalation = {
                'low': 'medium',
                'medium': 'high',
                'high': 'urgent',
                'urgent': 'urgent'  # Already at max priority
            }

            new_priority = priority_escalation.get(request.priority, request.priority)

            # Update the request priority
            old_priority = request.priority
            request.priority = new_priority
            request.save()

            # Schedule escalation notification
            NotificationService.schedule_escalation(
                instance=request,
                event_type=f'SLA breach - priority escalated from {old_priority} to {new_priority}',
                escalation_hours=1  # Notify immediately
            )

            # Log the escalation
            from workflows.services.audit import AuditLogService
            AuditLogService.log_event(
                instance_type='MaintenanceRequest',
                instance_id=str(request.id),
                event_type='escalation',
                event_name='sla_breach_escalation',
                user=None,  # System action
                metadata={
                    'old_priority': old_priority,
                    'new_priority': new_priority,
                    'sla_breached': True,
                    'escalation_reason': 'SLA threshold exceeded'
                },
                notes=f'Priority escalated from {old_priority} to {new_priority} due to SLA breach'
            )

            return True

        except Exception as e:
            logger.error(f"Failed to escalate request {request.id}: {e}")
            return False
