"""
Workflow Trigger Service
Handles automated workflow triggers and actions
"""

from typing import List, Dict, Any, Optional
from django.db import models
from django.utils import timezone
import logging

from ..models import WorkflowTrigger

logger = logging.getLogger(__name__)


class WorkflowTriggerService:
    """
    Service for managing automated workflow triggers
    """

    @staticmethod
    def process_triggers_for_instance(instance: models.Model,
                                    event: str = None,
                                    event_data: Dict[str, Any] = None,
                                    user = None) -> List[Dict[str, Any]]:
        """
        Process all active triggers for a given instance
        """
        results = []

        try:
            # Get active triggers for this instance type
            triggers = WorkflowTrigger.objects.filter(
                instance_type=instance.__class__.__name__,
                is_active=True
            ).order_by('priority')

            for trigger in triggers:
                try:
                    # Check if trigger should fire
                    if trigger.should_trigger(instance, {'event': event, **(event_data or {})}):
                        # Execute the action
                        success = trigger.execute_action(instance, user)

                        # Update last triggered time
                        trigger.last_triggered = timezone.now()
                        trigger.save()

                        results.append({
                            'trigger_id': trigger.id,
                            'trigger_name': trigger.name,
                            'success': success,
                            'action_type': trigger.action_type
                        })

                        # Log the trigger execution
                        from .audit import AuditLogService
                        AuditLogService.log_event(
                            instance_type=instance.__class__.__name__,
                            instance_id=str(instance.id),
                            event_type='trigger',
                            event_name=f'trigger_executed_{trigger.action_type}',
                            user=user,
                            metadata={
                                'trigger_id': trigger.id,
                                'trigger_name': trigger.name,
                                'action_type': trigger.action_type,
                                'success': success
                            },
                            notes=f'Workflow trigger "{trigger.name}" executed with {"success" if success else "failure"}'
                        )

                except Exception as e:
                    logger.error(f"Error processing trigger {trigger.id}: {e}")
                    results.append({
                        'trigger_id': trigger.id,
                        'trigger_name': trigger.name,
                        'success': False,
                        'error': str(e)
                    })

        except Exception as e:
            logger.error(f"Error processing triggers for {instance.__class__.__name__} {instance.id}: {e}")

        return results

    @staticmethod
    def create_trigger(name: str,
                      instance_type: str,
                      trigger_type: str,
                      action_type: str,
                      trigger_config: Dict[str, Any],
                      action_config: Dict[str, Any],
                      user = None) -> WorkflowTrigger:
        """
        Create a new workflow trigger
        """
        try:
            trigger = WorkflowTrigger.objects.create(
                name=name,
                instance_type=instance_type,
                trigger_type=trigger_type,
                action_type=action_type,
                created_by=user,

                # Time-based settings
                time_delay_hours=trigger_config.get('time_delay_hours'),
                time_delay_field=trigger_config.get('time_delay_field'),

                # Condition-based settings
                condition_field=trigger_config.get('condition_field'),
                condition_type=trigger_config.get('condition_type'),
                condition_value=trigger_config.get('condition_value'),

                # Action settings
                action_data=action_config
            )

            logger.info(f"Created workflow trigger: {name}")
            return trigger

        except Exception as e:
            logger.error(f"Failed to create workflow trigger: {e}")
            raise

    @staticmethod
    def get_active_triggers(instance_type: str = None) -> List[WorkflowTrigger]:
        """
        Get all active triggers, optionally filtered by instance type
        """
        queryset = WorkflowTrigger.objects.filter(is_active=True)

        if instance_type:
            queryset = queryset.filter(instance_type=instance_type)

        return list(queryset.order_by('priority'))

    @staticmethod
    def deactivate_trigger(trigger_id: int, user = None) -> bool:
        """
        Deactivate a workflow trigger
        """
        try:
            trigger = WorkflowTrigger.objects.get(id=trigger_id)
            trigger.is_active = False
            trigger.save()

            # Log deactivation
            from .audit import AuditLogService
            AuditLogService.log_event(
                instance_type='WorkflowTrigger',
                instance_id=str(trigger_id),
                event_type='manual',
                event_name='trigger_deactivated',
                user=user,
                metadata={'trigger_name': trigger.name},
                notes=f'Workflow trigger "{trigger.name}" deactivated'
            )

            return True

        except WorkflowTrigger.DoesNotExist:
            return False
        except Exception as e:
            logger.error(f"Failed to deactivate trigger {trigger_id}: {e}")
            return False
