"""
Maintenance Workflow Engine
Handles maintenance request state transitions and validations
"""

from typing import Dict, List, Any, Tuple, Optional
from django.core.exceptions import ValidationError
from django.utils import timezone
from .base import WorkflowEngine, WorkflowTransition, WorkflowTransitionError
from maintenance.models import MaintenanceRequest, MaintenanceStatus, Priority


class MaintenanceWorkflowEngine(WorkflowEngine):
    """
    Workflow engine for maintenance requests
    Handles state transitions, validations, and business rules
    """

    def _get_status_field(self) -> str:
        return 'status'

    def _define_transitions(self) -> Dict[str, WorkflowTransition]:
        """Define all possible maintenance workflow transitions"""

        return {
            'assign_technician': WorkflowTransition(
                from_states=['pending'],
                to_state='in_progress',
                event='assign_technician',
                required_permissions=['superuser', 'group:Manager', 'role:caretaker'],  # Managers, caretakers, and superusers can assign
                validators=[
                    self._validate_technician_assignment,
                    self._validate_not_overdue,
                ],
                side_effects=[
                    self._set_assigned_date,
                    self._schedule_follow_up,
                ],
                description='Assign a technician to the maintenance request'
            ),

            'start_work': WorkflowTransition(
                from_states=['in_progress'],
                to_state='in_progress',  # State stays the same, but marks work started
                event='start_work',
                required_permissions=['superuser', 'group:Manager', 'staff'],
                validators=[
                    self._validate_technician_assigned,
                ],
                side_effects=[
                    self._log_work_started,
                ],
                description='Mark work as started'
            ),

            'complete_request': WorkflowTransition(
                from_states=['in_progress'],
                to_state='completed',
                event='complete_request',
                required_permissions=['superuser', 'group:Manager', 'role:caretaker'],  # Managers, caretakers, and superusers can close
                validators=[
                    self._validate_technician_assigned,
                    self._validate_completion_data,
                ],
                side_effects=[
                    self._set_completion_date,
                    self._calculate_cost_variance,
                    self._schedule_tenant_feedback,
                ],
                description='Mark the maintenance request as completed'
            ),

            'cancel_request': WorkflowTransition(
                from_states=['pending', 'in_progress'],
                to_state='cancelled',
                event='cancel_request',
                required_permissions=['superuser', 'group:Manager', 'role:caretaker'],  # Managers, caretakers, and superusers can cancel
                validators=[
                    self._validate_cancellation_reason,
                ],
                side_effects=[
                    self._log_cancellation,
                ],
                description='Cancel the maintenance request'
            ),

            'reopen_request': WorkflowTransition(
                from_states=['completed', 'cancelled'],
                to_state='pending',
                event='reopen_request',
                required_permissions=['superuser', 'group:Manager', 'role:caretaker'],  # Managers, caretakers, and superusers can reopen
                validators=[
                    self._validate_reopen_eligibility,
                ],
                side_effects=[
                    self._reset_assignment_data,
                    self._log_reopen_reason,
                ],
                description='Reopen a completed or cancelled request'
            ),

            'escalate_priority': WorkflowTransition(
                from_states=['pending', 'in_progress'],
                to_state='pending',  # State stays the same, priority changes
                event='escalate_priority',
                required_permissions=['superuser', 'group:Manager', 'role:manager'],  # Managers and superusers can escalate priority
                validators=[
                    self._validate_priority_escalation,
                ],
                side_effects=[
                    self._update_priority,
                    self._schedule_urgent_response,
                ],
                description='Escalate the priority of the maintenance request'
            ),

            'schedule_maintenance': WorkflowTransition(
                from_states=['pending'],
                to_state='pending',  # State stays the same, but scheduled
                event='schedule_maintenance',
                required_permissions=['superuser', 'group:Manager', 'role:caretaker'],  # Managers, caretakers, and superusers can schedule
                validators=[
                    self._validate_scheduling_data,
                ],
                side_effects=[
                    self._set_scheduled_date,
                ],
                description='Schedule maintenance for a specific date'
            ),
        }

    def _get_available_events(self, user) -> List[str]:
        """Get events available to the current user based on their role"""
        available_events = []

        # Check if user is superuser or in Manager group
        is_manager_or_superuser = (
            user.is_superuser or
            user.groups.filter(name='Manager').exists()
        )

        try:
            staff_profile = user.staff_profile
            user_role = staff_profile.role if staff_profile and staff_profile.is_active_staff else None
        except AttributeError:
            user_role = None

        # Define role-based permissions for maintenance workflow
        event_permissions = {
            # Assignment and basic operations - caretakers and above, or managers/superusers
            'assign_technician': user_role in ['manager', 'caretaker'] or is_manager_or_superuser,
            'schedule_maintenance': user_role in ['manager', 'caretaker'] or is_manager_or_superuser,
            'start_work': user_role in ['manager', 'caretaker', 'maintenance'] or is_manager_or_superuser,

            # Approval/closure operations - only managers, caretakers, or superusers
            'complete_request': user_role in ['manager', 'caretaker'] or is_manager_or_superuser,
            'cancel_request': user_role in ['manager', 'caretaker'] or is_manager_or_superuser,
            'reopen_request': user_role in ['manager', 'caretaker'] or is_manager_or_superuser,

            # Escalation - managers or superusers only
            'escalate_priority': user_role == 'manager' or is_manager_or_superuser,
        }

        # Check each transition - for UI display, only check permissions and state, not parameters
        for event, has_permission in event_permissions.items():
            if has_permission and event in self.transitions:
                transition = self.transitions[event]
                current_state = self.get_current_state()

                # Check if current state allows this transition
                if current_state in transition.from_states:
                    available_events.append(event)

        return available_events

    # Validation Methods

    def _validate_technician_assignment(self, instance: MaintenanceRequest, user, **kwargs) -> Tuple[bool, str]:
        """Validate technician assignment"""
        technician_name = kwargs.get('technician_name')
        if not technician_name or not technician_name.strip():
            return False, "Technician name is required"

        if len(technician_name.strip()) < 2:
            return False, "Technician name must be at least 2 characters"

        return True, "OK"

    def _validate_not_overdue(self, instance: MaintenanceRequest, user, **kwargs) -> Tuple[bool, str]:
        """Validate request is not severely overdue"""
        if instance.is_overdue and instance.days_pending > 30:
            return False, "Request is too overdue for assignment. Consider escalation first."

        return True, "OK"

    def _validate_technician_assigned(self, instance: MaintenanceRequest, user, **kwargs) -> Tuple[bool, str]:
        """Validate that a technician is assigned"""
        if not instance.assigned_to:
            return False, "No technician assigned to this request"

        return True, "OK"

    def _validate_completion_data(self, instance: MaintenanceRequest, user, **kwargs) -> Tuple[bool, str]:
        """Validate completion data"""
        resolution_notes = kwargs.get('resolution_notes')
        if not resolution_notes or not resolution_notes.strip():
            return False, "Resolution notes are required to complete the request"

        return True, "OK"

    def _validate_cancellation_reason(self, instance: MaintenanceRequest, user, **kwargs) -> Tuple[bool, str]:
        """Validate cancellation has a reason"""
        reason = kwargs.get('reason')
        if not reason or not reason.strip():
            return False, "Cancellation reason is required"
        return True, "OK"

    def _validate_reopen_eligibility(self, instance: MaintenanceRequest, user, **kwargs) -> Tuple[bool, str]:
        """Validate request can be reopened"""
        if instance.status == 'completed':
            # Can reopen completed requests within 30 days
            if instance.completed_date:
                days_since_completion = (timezone.now() - instance.completed_date).days
                if days_since_completion > 30:
                    return False, "Cannot reopen requests completed more than 30 days ago"

        return True, "OK"

    def _validate_priority_escalation(self, instance: MaintenanceRequest, user, **kwargs) -> Tuple[bool, str]:
        """Validate priority escalation"""
        current_priority = instance.priority
        priority_order = ['low', 'medium', 'high', 'urgent']

        try:
            current_index = priority_order.index(current_priority)
            if current_index >= len(priority_order) - 1:
                return False, "Request is already at maximum priority"
        except ValueError:
            return False, "Invalid current priority"

        return True, "OK"

    def _validate_scheduling_data(self, instance: MaintenanceRequest, user, **kwargs) -> Tuple[bool, str]:
        """Validate scheduling data"""
        # This would validate the scheduled_date in kwargs
        return True, "OK"

    # Side Effect Methods

    def _set_assigned_date(self, instance: MaintenanceRequest, user, **kwargs):
        """Set assignment date and technician"""
        technician_name = kwargs.get('technician_name')
        if technician_name:
            instance.assigned_to = technician_name
        instance.assigned_date = timezone.now()
        instance.save(update_fields=['assigned_to', 'assigned_date'])

    def _schedule_follow_up(self, instance: MaintenanceRequest, user, **kwargs):
        """Schedule follow-up based on priority"""
        if instance.priority == Priority.URGENT:
            days = 1
        elif instance.priority == Priority.HIGH:
            days = 3
        elif instance.priority == Priority.MEDIUM:
            days = 7
        else:
            days = 14

        instance.follow_up_date = timezone.now() + timezone.timedelta(days=days)
        instance.save(update_fields=['follow_up_date'])

    def _log_work_started(self, instance: MaintenanceRequest, user, **kwargs):
        """Log work started"""
        from .services import AuditLogService
        AuditLogService.log_event(
            instance_type='MaintenanceRequest',
            instance_id=str(instance.id),
            event_type='manual',
            event_name='work_started',
            user=user,
            notes=f"Work started on maintenance request by {user.get_full_name()}",
        )

    def _set_completion_date(self, instance: MaintenanceRequest, user, **kwargs):
        """Set completion date, notes, and cost"""
        resolution_notes = kwargs.get('resolution_notes')
        actual_cost = kwargs.get('actual_cost')

        instance.completed_date = timezone.now()
        if resolution_notes:
            instance.resolution_notes = resolution_notes
        if actual_cost is not None:
            instance.actual_cost = actual_cost

        instance.save(update_fields=['completed_date', 'resolution_notes', 'actual_cost'])

    def _calculate_cost_variance(self, instance: MaintenanceRequest, user, **kwargs):
        """Calculate and save cost variance"""
        if instance.estimated_cost and instance.actual_cost:
            instance.save(update_fields=['estimated_cost', 'actual_cost'])

    def _schedule_tenant_feedback(self, instance: MaintenanceRequest, user, **kwargs):
        """Schedule tenant feedback request"""
        # Could trigger email/SMS to tenant for feedback
        from .services import NotificationService

        # Schedule notification for tenant feedback in 24 hours
        try:
            feedback_notification = NotificationService._create_notification(
                recipient=instance.tenant.user if hasattr(instance.tenant, 'user') else user,
                instance=instance,
                event='feedback_request',
                config={
                    'title': 'Please Rate Our Service',
                    'template': 'tenant_feedback',
                    'priority': 'low',
                },
                event_data={}
            )

            if feedback_notification:
                # Schedule for tomorrow
                feedback_notification.next_escalation = timezone.now() + timezone.timedelta(days=1)
                feedback_notification.save()

        except Exception as e:
            # Don't fail the workflow if notification fails
            pass

    def _log_cancellation(self, instance: MaintenanceRequest, user, **kwargs):
        """Log cancellation with reason"""
        reason = kwargs.get('reason', 'No reason provided')

        # Set cancellation reason on instance if it has a field for it
        if hasattr(instance, 'cancellation_reason'):
            instance.cancellation_reason = reason
            instance.save(update_fields=['cancellation_reason'])

        from .services import AuditLogService

        AuditLogService.log_event(
            instance_type='MaintenanceRequest',
            instance_id=str(instance.id),
            event_type='manual',
            event_name='request_cancelled',
            user=user,
            notes=f"Request cancelled: {reason}",
            metadata={'cancellation_reason': reason}
        )

    def _reset_assignment_data(self, instance: MaintenanceRequest, user, **kwargs):
        """Reset assignment data when reopening"""
        instance.assigned_to = None
        instance.assigned_date = None
        instance.follow_up_date = None
        instance.save(update_fields=['assigned_to', 'assigned_date', 'follow_up_date'])

    def _log_reopen_reason(self, instance: MaintenanceRequest, user, **kwargs):
        """Log reason for reopening"""
        reason = kwargs.get('reason', 'No reason provided')
        from .services import AuditLogService

        AuditLogService.log_event(
            instance_type='MaintenanceRequest',
            instance_id=str(instance.id),
            event_type='manual',
            event_name='request_reopened',
            user=user,
            notes=f"Request reopened: {reason}",
            metadata={'reopen_reason': reason}
        )

    def _update_priority(self, instance: MaintenanceRequest, user, **kwargs):
        """Update priority to specified level or next level"""
        new_priority = kwargs.get('new_priority')
        if new_priority and new_priority in ['low', 'medium', 'high', 'urgent']:
            # Set to specific priority
            instance.priority = new_priority
            instance.save(update_fields=['priority'])
        else:
            # Auto-escalate to next level
            priority_order = ['low', 'medium', 'high', 'urgent']
            try:
                current_index = priority_order.index(instance.priority)
                if current_index < len(priority_order) - 1:
                    instance.priority = priority_order[current_index + 1]
                    instance.save(update_fields=['priority'])
            except (ValueError, IndexError):
                pass  # Keep current priority if something goes wrong

    def _schedule_urgent_response(self, instance: MaintenanceRequest, user, **kwargs):
        """Schedule urgent response for escalated requests"""
        if instance.priority == Priority.URGENT:
            # Schedule immediate follow-up
            instance.follow_up_date = timezone.now() + timezone.timedelta(hours=4)
            instance.save(update_fields=['follow_up_date'])

            # Trigger escalation notifications
            from .services import NotificationService
            NotificationService.schedule_escalation(
                instance=instance,
                event_type='urgent_maintenance',
                escalation_hours=2,
                priority='urgent'
            )

    def _set_scheduled_date(self, instance: MaintenanceRequest, user, **kwargs):
        """Set scheduled date from kwargs"""
        scheduled_date = kwargs.get('scheduled_date')
        if scheduled_date:
            instance.scheduled_date = scheduled_date
            instance.save(update_fields=['scheduled_date'])

    # Additional Workflow Methods

    def get_sla_status(self) -> Dict[str, Any]:
        """Get SLA status for the maintenance request"""
        if self.instance.status == MaintenanceStatus.COMPLETED:
            return {
                'status': 'completed',
                'days_to_complete': self.instance.days_to_completion,
                'was_on_time': self.instance.days_to_completion <= self._get_sla_days(),
            }
        elif self.instance.is_overdue:
            return {
                'status': 'overdue',
                'days_overdue': self.instance.days_pending - self._get_sla_days(),
                'sla_days': self._get_sla_days(),
            }
        else:
            return {
                'status': 'on_track',
                'days_remaining': max(0, self._get_sla_days() - self.instance.days_pending),
                'sla_days': self._get_sla_days(),
            }

    def _get_sla_days(self) -> int:
        """Get SLA days based on priority"""
        sla_days = {
            Priority.URGENT: 1,
            Priority.HIGH: 3,
            Priority.MEDIUM: 7,
            Priority.LOW: 14,
        }
        return sla_days.get(self.instance.priority, 7)

    def can_request_feedback(self) -> bool:
        """Check if tenant feedback can be requested"""
        if self.instance.status != MaintenanceStatus.COMPLETED:
            return False

        if not self.instance.completed_date:
            return False

        # Can request feedback within 7 days of completion
        days_since_completion = (timezone.now() - self.instance.completed_date).days
        return days_since_completion <= 7

    def get_workflow_metrics(self) -> Dict[str, Any]:
        """Get workflow metrics for reporting"""
        return {
            'current_state': self.get_current_state(),
            'days_in_current_state': self._calculate_days_in_state(),
            'total_transitions': len(self.get_workflow_history()),
            'assigned_duration': self._calculate_assigned_duration(),
            'sla_status': self.get_sla_status(),
        }

    def _calculate_days_in_state(self) -> int:
        """Calculate days in current state"""
        # This would require tracking state change timestamps
        # For now, return days since creation if pending, or days since assignment if in progress
        if self.instance.status == MaintenanceStatus.PENDING:
            return self.instance.days_pending
        elif self.instance.status == MaintenanceStatus.IN_PROGRESS:
            if self.instance.assigned_date:
                return (timezone.now() - self.instance.assigned_date).days
            else:
                return self.instance.days_pending
        return 0

    def _calculate_assigned_duration(self) -> Optional[int]:
        """Calculate total time assigned"""
        if self.instance.assigned_date and self.instance.completed_date:
            return (self.instance.completed_date - self.instance.assigned_date).days
        elif self.instance.assigned_date and self.instance.status == MaintenanceStatus.IN_PROGRESS:
            return (timezone.now() - self.instance.assigned_date).days
        return None
