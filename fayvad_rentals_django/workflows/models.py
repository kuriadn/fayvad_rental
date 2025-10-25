"""
Workflow models for triggers and automated transitions
"""

from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class WorkflowTrigger(models.Model):
    """
    Model for automated workflow triggers
    """

    TRIGGER_TYPES = [
        ('time_based', 'Time Based'),
        ('event_based', 'Event Based'),
        ('condition_based', 'Condition Based'),
    ]

    CONDITION_TYPES = [
        ('equals', 'Equals'),
        ('not_equals', 'Not Equals'),
        ('greater_than', 'Greater Than'),
        ('less_than', 'Less Than'),
        ('contains', 'Contains'),
        ('not_contains', 'Does Not Contain'),
    ]

    ACTION_TYPES = [
        ('transition', 'State Transition'),
        ('notification', 'Send Notification'),
        ('escalation', 'Escalate Priority'),
        ('assignment', 'Auto Assign'),
    ]

    # Trigger configuration
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    trigger_type = models.CharField(max_length=20, choices=TRIGGER_TYPES)
    instance_type = models.CharField(max_length=100)  # Model class name

    # Time-based trigger settings
    time_delay_hours = models.PositiveIntegerField(null=True, blank=True)
    time_delay_field = models.CharField(max_length=100, null=True, blank=True)  # e.g., 'created_at'

    # Condition-based trigger settings
    condition_field = models.CharField(max_length=100, null=True, blank=True)
    condition_type = models.CharField(max_length=20, choices=CONDITION_TYPES, null=True, blank=True)
    condition_value = models.CharField(max_length=200, null=True, blank=True)

    # Action configuration
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    action_data = models.JSONField(default=dict)  # Action-specific data

    # Control
    is_active = models.BooleanField(default=True)
    priority = models.PositiveIntegerField(default=10)  # Execution order

    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    last_triggered = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['priority', 'created_at']

    def __str__(self):
        return f"{self.name} ({self.get_trigger_type_display()})"

    def should_trigger(self, instance, event_data=None):
        """Check if this trigger should fire for the given instance"""
        try:
            if self.trigger_type == 'time_based':
                return self._check_time_based_trigger(instance)
            elif self.trigger_type == 'event_based':
                return self._check_event_based_trigger(instance, event_data)
            elif self.trigger_type == 'condition_based':
                return self._check_condition_based_trigger(instance)
            return False
        except Exception:
            return False

    def _check_time_based_trigger(self, instance):
        """Check if time-based trigger should fire"""
        if not self.time_delay_hours or not self.time_delay_field:
            return False

        # Get the timestamp field value
        field_value = getattr(instance, self.time_delay_field, None)
        if not field_value:
            return False

        # Check if enough time has passed
        trigger_time = field_value + timezone.timedelta(hours=self.time_delay_hours)
        return timezone.now() >= trigger_time

    def _check_event_based_trigger(self, instance, event_data):
        """Check if event-based trigger should fire"""
        # Event-based triggers fire on specific workflow events
        # This would be configured in action_data
        trigger_events = self.action_data.get('trigger_events', [])
        current_event = event_data.get('event') if event_data else None

        return current_event in trigger_events

    def _check_condition_based_trigger(self, instance):
        """Check if condition-based trigger should fire"""
        if not self.condition_field or not self.condition_type:
            return False

        # Get field value
        field_value = getattr(instance, self.condition_field, None)
        if field_value is None:
            return False

        # Convert to string for comparison
        field_str = str(field_value)
        condition_value = self.condition_value or ''

        # Check condition
        if self.condition_type == 'equals':
            return field_str == condition_value
        elif self.condition_type == 'not_equals':
            return field_str != condition_value
        elif self.condition_type == 'greater_than':
            return field_str > condition_value
        elif self.condition_type == 'less_than':
            return field_str < condition_value
        elif self.condition_type == 'contains':
            return condition_value in field_str
        elif self.condition_type == 'not_contains':
            return condition_value not in field_str

        return False

    def execute_action(self, instance, user=None):
        """Execute the configured action"""
        try:
            if self.action_type == 'transition':
                return self._execute_transition(instance, user)
            elif self.action_type == 'notification':
                return self._execute_notification(instance, user)
            elif self.action_type == 'escalation':
                return self._execute_escalation(instance, user)
            elif self.action_type == 'assignment':
                return self._execute_assignment(instance, user)
            return False
        except Exception as e:
            # Log error but don't raise
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to execute workflow trigger action: {e}")
            return False

    def _execute_transition(self, instance, user):
        """Execute state transition"""
        new_state = self.action_data.get('new_state')
        if not new_state:
            return False

        # Use workflow engine to transition
        if hasattr(instance, 'transition'):
            result = instance.transition(new_state, user)
            return result.get('success', False)

        # Direct state change for simple models
        old_state = getattr(instance, 'status', None)
        setattr(instance, 'status', new_state)
        instance.save()

        # Log the transition
        from .services.audit import AuditLogService
        AuditLogService.log_workflow_transition(
            instance_type=instance.__class__.__name__,
            instance_id=str(instance.id),
            event='auto_transition',
            old_state=old_state,
            new_state=new_state,
            user=user,
            metadata={'trigger_id': self.id},
            notes=f'Auto-transition triggered by {self.name}'
        )

        return True

    def _execute_notification(self, instance, user):
        """Execute notification action"""
        from .services.notifications import NotificationService

        notification_config = self.action_data.get('notification', {})
        NotificationService.notify_workflow_transition(
            instance=instance,
            event='auto_notification',
            user=user,
            **notification_config
        )
        return True

    def _execute_escalation(self, instance, user):
        """Execute escalation action"""
        from .services.notifications import NotificationService

        escalation_hours = self.action_data.get('escalation_hours', 24)
        NotificationService.schedule_escalation(
            instance=instance,
            event_type=f'Auto-escalation: {self.name}',
            escalation_hours=escalation_hours
        )
        return True

    def _execute_assignment(self, instance, user):
        """Execute auto-assignment action"""
        assignee_field = self.action_data.get('assignee_field', 'assigned_to')
        assignee_id = self.action_data.get('assignee_id')

        if assignee_id and hasattr(instance, assignee_field):
            # Get assignee
            try:
                assignee = User.objects.get(id=assignee_id)
                setattr(instance, assignee_field, assignee)
                instance.save()
                return True
            except User.DoesNotExist:
                pass

        return False
