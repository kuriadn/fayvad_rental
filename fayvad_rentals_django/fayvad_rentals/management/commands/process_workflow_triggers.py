"""
Management command to process automated workflow triggers
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import logging

from workflows.services.triggers import WorkflowTriggerService
from maintenance.models import MaintenanceRequest
from payments.models import Payment
from tenants.models import Tenant

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Process automated workflow triggers'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be triggered without actually executing',
        )
        parser.add_argument(
            '--instance-type',
            type=str,
            help='Process triggers for specific instance type only',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        instance_type_filter = options['instance_type']

        if dry_run:
            self.stdout.write('DRY RUN MODE - No actions will be executed')

        # Define instance types to check
        instance_types = [
            ('MaintenanceRequest', MaintenanceRequest),
            ('Payment', Payment),
            ('Tenant', Tenant),
        ]

        total_triggers_executed = 0

        for instance_type_name, model_class in instance_types:
            if instance_type_filter and instance_type_filter != instance_type_name:
                continue

            self.stdout.write(f'Processing triggers for {instance_type_name}...')

            # Get recent instances to check (last 24 hours to avoid processing too many)
            since_date = timezone.now() - timedelta(hours=24)

            # Get instances that might need trigger processing
            instances = model_class.objects.filter(
                # Add any relevant filters here
                # For now, process all recent instances
            )

            # For time-based triggers, we might want to limit to recently modified instances
            if hasattr(model_class, 'updated_at'):
                instances = instances.filter(updated_at__gte=since_date)
            elif hasattr(model_class, 'created_at'):
                instances = instances.filter(created_at__gte=since_date)

            # Limit to prevent excessive processing
            instances = instances[:100]  # Process max 100 instances per type

            for instance in instances:
                try:
                    if dry_run:
                        # Just show what would be triggered
                        triggers = WorkflowTriggerService.get_active_triggers(instance_type_name)
                        triggered = []

                        for trigger in triggers:
                            if trigger.should_trigger(instance):
                                triggered.append(trigger.name)

                        if triggered:
                            self.stdout.write(
                                f'  WOULD TRIGGER for {instance_type_name} {instance.id}: {", ".join(triggered)}'
                            )
                    else:
                        # Actually process triggers
                        results = WorkflowTriggerService.process_triggers_for_instance(
                            instance=instance,
                            event='periodic_check'
                        )

                        successful_triggers = [r for r in results if r.get('success')]
                        if successful_triggers:
                            total_triggers_executed += len(successful_triggers)
                            trigger_names = [r['trigger_name'] for r in successful_triggers]
                            self.stdout.write(
                                f'  TRIGGERED for {instance_type_name} {instance.id}: {", ".join(trigger_names)}'
                            )

                        failed_triggers = [r for r in results if not r.get('success')]
                        if failed_triggers:
                            for failed in failed_triggers:
                                self.stdout.write(
                                    self.style.WARNING(f'  FAILED TRIGGER for {instance_type_name} {instance.id}: {failed["trigger_name"]}')
                                )

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'  ERROR processing {instance_type_name} {instance.id}: {e}')
                    )

        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully executed {total_triggers_executed} workflow triggers')
            )
