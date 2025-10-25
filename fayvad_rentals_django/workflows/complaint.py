"""
Complaint Workflow Engine
Handles complaint lifecycle from submission to resolution
"""

from typing import Dict, List, Any, Tuple, Optional
from django.core.exceptions import ValidationError
from django.utils import timezone
from .base import WorkflowEngine, WorkflowTransition, WorkflowTransitionError
from tenants.models import Complaint, ComplaintStatus, ComplaintPriority

class ComplaintWorkflowEngine(WorkflowEngine):
    """
    Workflow engine for complaint management
    Handles status transitions and SLA tracking for tenant complaints
    """

    def _get_status_field(self) -> str:
        return 'status'

    def _define_transitions(self) -> Dict[str, WorkflowTransition]:
        """Define all possible complaint workflow transitions"""

        return {
            'submit_complaint': WorkflowTransition(
                from_states=[],  # Can submit new complaints
                to_state='open',
                event='submit_complaint',
                required_permissions=[],  # Any user can submit
                validators=[
                    self._validate_complaint_details,
                    self._validate_tenant_eligibility,
                ],
                side_effects=[
                    self._generate_complaint_number,
                    self._set_escalation_deadline,
                    self._log_complaint_submission,
                    self._notify_acknowledgment,
                ],
                description='Submit a new complaint'
            ),

            'assign_investigator': WorkflowTransition(
                from_states=['open'],
                to_state='investigating',
                event='assign_investigator',
                required_permissions=['role:caretaker'],  # Staff can assign
                validators=[
                    self._validate_assignment_eligibility,
                ],
                side_effects=[
                    self._assign_staff_member,
                    self._log_assignment,
                    self._notify_assigned_staff,
                    self._notify_tenant_assignment,
                ],
                description='Assign staff member to investigate complaint'
            ),

            'update_priority': WorkflowTransition(
                from_states=['open', 'investigating'],
                to_state=None,  # Status stays the same
                event='update_priority',
                required_permissions=['role:caretaker'],  # Staff can update priority
                validators=[
                    self._validate_priority_change,
                ],
                side_effects=[
                    self._update_complaint_priority,
                    self._adjust_escalation_deadline,
                    self._log_priority_change,
                    self._notify_priority_update,
                ],
                description='Update complaint priority level'
            ),

            'request_more_info': WorkflowTransition(
                from_states=['investigating'],
                to_state='investigating',  # Status stays investigating
                event='request_more_info',
                required_permissions=['role:caretaker'],  # Staff can request info
                validators=[
                    self._validate_info_request,
                ],
                side_effects=[
                    self._log_info_request,
                    self._extend_escalation_deadline,
                    self._notify_tenant_info_request,
                ],
                description='Request additional information from tenant'
            ),

            'resolve_complaint': WorkflowTransition(
                from_states=['open', 'investigating'],
                to_state='resolved',
                event='resolve_complaint',
                required_permissions=['role:caretaker'],  # Staff can resolve
                validators=[
                    self._validate_resolution_details,
                ],
                side_effects=[
                    self._set_resolution_date,
                    self._log_resolution,
                    self._notify_tenant_resolution,
                ],
                description='Resolve the complaint with solution'
            ),

            'escalate_complaint': WorkflowTransition(
                from_states=['open', 'investigating'],
                to_state='investigating',  # Status stays investigating but escalated
                event='escalate_complaint',
                required_permissions=['role:caretaker'],  # Staff can escalate
                validators=[
                    self._validate_escalation_eligibility,
                ],
                side_effects=[
                    self._increase_priority,
                    self._adjust_escalation_deadline,
                    self._notify_management_escalation,
                    self._log_escalation,
                ],
                description='Escalate complaint to higher priority'
            ),

            'close_complaint': WorkflowTransition(
                from_states=['resolved'],
                to_state='closed',
                event='close_complaint',
                required_permissions=['role:caretaker'],  # Staff can close
                validators=[
                    self._validate_closure_eligibility,
                ],
                side_effects=[
                    self._log_closure,
                    self._notify_tenant_closure,
                ],
                description='Close the complaint after resolution'
            ),

            'reopen_complaint': WorkflowTransition(
                from_states=['closed'],
                to_state='open',
                event='reopen_complaint',
                required_permissions=[],  # Any user can reopen
                validators=[
                    self._validate_reopen_eligibility,
                ],
                side_effects=[
                    self._reset_escalation_deadline,
                    self._log_reopen,
                    self._notify_staff_reopen,
                ],
                description='Reopen a previously closed complaint'
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

        # Check if user is the complaint tenant
        is_complaint_tenant = (
            hasattr(self.instance, 'tenant') and
            self.instance.tenant and
            hasattr(self.instance.tenant, 'user') and
            self.instance.tenant.user == user
        )

        # Define role-based permissions for complaint workflow
        event_permissions = {
            # Staff actions - caretakers and above, or managers/superusers
            'assign_investigator': user_role in ['manager', 'caretaker'] or is_manager_or_superuser,
            'update_priority': user_role in ['manager', 'caretaker'] or is_manager_or_superuser,
            'request_more_info': user_role in ['manager', 'caretaker'] or is_manager_or_superuser,
            'resolve_complaint': user_role in ['manager', 'caretaker'] or is_manager_or_superuser,
            'escalate_complaint': user_role in ['manager', 'caretaker'] or is_manager_or_superuser,
            'close_complaint': user_role in ['manager', 'caretaker'] or is_manager_or_superuser,

            # Tenant actions
            'submit_complaint': True,  # Any user can submit (for new complaints)
            'reopen_complaint': is_complaint_tenant,
        }

        # Check each transition - for UI display, only check permissions and state, not parameters
        for event, has_permission in event_permissions.items():
            if has_permission and event in self.transitions:
                transition = self.transitions[event]
                current_state = self.get_current_state()

                # Check if current state allows this transition
                if current_state in transition.from_states or (event == 'submit_complaint' and not self.instance.pk):
                    available_events.append(event)

        return available_events

    # Validation Methods

    def _validate_complaint_details(self, instance: Complaint, user, **kwargs) -> Tuple[bool, str]:
        """Validate complaint details"""
        if not instance.subject or not instance.subject.strip():
            return False, "Complaint subject is required"

        if not instance.description or not instance.description.strip():
            return False, "Complaint description is required"

        if len(instance.subject.strip()) < 5:
            return False, "Subject must be at least 5 characters"

        if len(instance.description.strip()) < 10:
            return False, "Description must be at least 10 characters"

        return True, "OK"

    def _validate_tenant_eligibility(self, instance: Complaint, user, **kwargs) -> Tuple[bool, str]:
        """Validate tenant can submit complaints"""
        if not instance.tenant:
            return False, "Tenant is required"

        # Check if tenant is active or former (can still complain about past issues)
        if instance.tenant.status not in ['active', 'former']:
            return False, f"Tenant status '{instance.tenant.status}' does not allow complaints"

        return True, "OK"

    def _validate_assignment_eligibility(self, instance: Complaint, user, **kwargs) -> Tuple[bool, str]:
        """Validate complaint can be assigned"""
        assignee_id = kwargs.get('assignee_id')
        if not assignee_id:
            return False, "Assignee is required"

        return True, "OK"

    def _validate_priority_change(self, instance: Complaint, user, **kwargs) -> Tuple[bool, str]:
        """Validate priority change"""
        new_priority = kwargs.get('new_priority')
        if not new_priority or new_priority not in ['low', 'medium', 'high', 'urgent']:
            return False, "Valid priority level is required"

        return True, "OK"

    def _validate_info_request(self, instance: Complaint, user, **kwargs) -> Tuple[bool, str]:
        """Validate information request"""
        info_request = kwargs.get('info_request')
        if not info_request or not info_request.strip():
            return False, "Information request details are required"

        return True, "OK"

    def _validate_resolution_details(self, instance: Complaint, user, **kwargs) -> Tuple[bool, str]:
        """Validate resolution details"""
        resolution = kwargs.get('resolution')
        if not resolution or not resolution.strip():
            return False, "Resolution details are required"

        return True, "OK"

    def _validate_escalation_eligibility(self, instance: Complaint, user, **kwargs) -> Tuple[bool, str]:
        """Validate complaint can be escalated"""
        # Check if complaint has been open for more than priority-based threshold
        days_threshold = {
            'low': 14,      # 2 weeks
            'medium': 7,    # 1 week
            'high': 3,      # 3 days
            'urgent': 1,    # 1 day
        }

        threshold = days_threshold.get(instance.priority, 7)
        if instance.days_open < threshold:
            return False, f"Complaint must be open for at least {threshold} days before escalation (currently {instance.days_open} days)"

        return True, "OK"

    def _validate_closure_eligibility(self, instance: Complaint, user, **kwargs) -> Tuple[bool, str]:
        """Validate complaint can be closed"""
        if not instance.resolution:
            return False, "Complaint must be resolved before closing"

        if not instance.resolution_date:
            return False, "Resolution date is required for closure"

        return True, "OK"

    def _validate_reopen_eligibility(self, instance: Complaint, user, **kwargs) -> Tuple[bool, str]:
        """Validate complaint can be reopened"""
        # Check if closed within last 30 days
        if hasattr(instance, 'resolution_date') and instance.resolution_date:
            days_since_closure = (timezone.now() - instance.resolution_date).days
            if days_since_closure > 30:
                return False, "Complaints can only be reopened within 30 days of closure"

        return True, "OK"

    # Side Effect Methods

    def _generate_complaint_number(self, instance: Complaint, user, **kwargs):
        """Generate complaint number (handled in model save method)"""
        pass  # Model handles this automatically

    def _set_escalation_deadline(self, instance: Complaint, user, **kwargs):
        """Set escalation deadline based on priority"""
        from datetime import timedelta

        deadline_hours = {
            'low': 336,      # 14 days
            'medium': 168,   # 7 days
            'high': 72,      # 3 days
            'urgent': 24,    # 1 day
        }

        hours = deadline_hours.get(instance.priority, 168)  # Default to 7 days
        instance.escalation_deadline = timezone.now() + timedelta(hours=hours)
        instance.save(update_fields=['escalation_deadline'])

    def _log_complaint_submission(self, instance: Complaint, user, **kwargs):
        """Log complaint submission"""
        from .services import AuditLogService
        AuditLogService.log_event(
            instance_type='Complaint',
            instance_id=str(instance.id),
            event_type='submission',
            event_name='complaint_submitted',
            user=user,
            notes=f"Complaint submitted by {instance.tenant.name} - {instance.category_display}",
            metadata={
                'category': instance.category,
                'priority': instance.priority,
                'subject': instance.subject,
            }
        )

    def _notify_acknowledgment(self, instance: Complaint, user, **kwargs):
        """Send acknowledgment notification"""
        from .services import NotificationService
        if not instance.is_anonymous:
            NotificationService.create_notification(
                recipient=instance.tenant.user if hasattr(instance.tenant, 'user') else None,
                instance=instance,
                event='complaint_acknowledged',
                config={
                    'title': 'Complaint Received',
                    'template': 'complaint_acknowledged',
                    'priority': 'low',
                },
                event_data={}
            )

    def _assign_staff_member(self, instance: Complaint, user, **kwargs):
        """Assign staff member to complaint"""
        assignee_id = kwargs.get('assignee_id')
        if assignee_id:
            from accounts.models import Staff
            try:
                staff_member = Staff.objects.get(id=assignee_id)
                instance.assigned_to = staff_member
                instance.save(update_fields=['assigned_to'])
            except Staff.DoesNotExist:
                pass  # Handle gracefully

    def _log_assignment(self, instance: Complaint, user, **kwargs):
        """Log staff assignment"""
        from .services import AuditLogService
        assignee_name = instance.assigned_to.user.get_full_name() if instance.assigned_to else "Unassigned"
        AuditLogService.log_event(
            instance_type='Complaint',
            instance_id=str(instance.id),
            event_type='assignment',
            event_name='investigator_assigned',
            user=user,
            notes=f"Complaint assigned to {assignee_name}",
            metadata={
                'assignee_id': str(instance.assigned_to.id) if instance.assigned_to else None,
            }
        )

    def _notify_assigned_staff(self, instance: Complaint, user, **kwargs):
        """Notify assigned staff member"""
        from .services import NotificationService
        if instance.assigned_to:
            NotificationService.create_notification(
                recipient=instance.assigned_to.user,
                instance=instance,
                event='complaint_assigned',
                config={
                    'title': 'New Complaint Assigned',
                    'template': 'complaint_assigned',
                    'priority': 'medium',
                },
                event_data={}
            )

    def _notify_tenant_assignment(self, instance: Complaint, user, **kwargs):
        """Notify tenant of assignment"""
        from .services import NotificationService
        if not instance.is_anonymous and instance.contact_preference != 'no_contact':
            NotificationService.create_notification(
                recipient=instance.tenant.user if hasattr(instance.tenant, 'user') else None,
                instance=instance,
                event='complaint_assigned_tenant',
                config={
                    'title': 'Your Complaint is Being Investigated',
                    'template': 'complaint_assigned_tenant',
                    'priority': 'low',
                },
                event_data={}
            )

    def _update_complaint_priority(self, instance: Complaint, user, **kwargs):
        """Update complaint priority"""
        new_priority = kwargs.get('new_priority')
        if new_priority:
            instance.priority = new_priority
            instance.priority_changed = timezone.now()
            instance.save(update_fields=['priority', 'priority_changed'])

    def _adjust_escalation_deadline(self, instance: Complaint, user, **kwargs):
        """Adjust escalation deadline based on new priority"""
        self._set_escalation_deadline(instance, user, **kwargs)

    def _log_priority_change(self, instance: Complaint, user, **kwargs):
        """Log priority change"""
        from .services import AuditLogService
        new_priority = kwargs.get('new_priority')
        AuditLogService.log_event(
            instance_type='Complaint',
            instance_id=str(instance.id),
            event_type='priority_change',
            event_name='priority_updated',
            user=user,
            notes=f"Priority changed to {new_priority}",
            metadata={
                'old_priority': instance.priority,
                'new_priority': new_priority,
            }
        )

    def _notify_priority_update(self, instance: Complaint, user, **kwargs):
        """Notify tenant of priority update"""
        from .services import NotificationService
        if not instance.is_anonymous and instance.contact_preference != 'no_contact':
            NotificationService.create_notification(
                recipient=instance.tenant.user if hasattr(instance.tenant, 'user') else None,
                instance=instance,
                event='complaint_priority_updated',
                config={
                    'title': 'Complaint Priority Updated',
                    'template': 'complaint_priority_updated',
                    'priority': 'low',
                },
                event_data=kwargs
            )

    def _log_info_request(self, instance: Complaint, user, **kwargs):
        """Log information request"""
        info_request = kwargs.get('info_request')
        from .services import AuditLogService
        AuditLogService.log_event(
            instance_type='Complaint',
            instance_id=str(instance.id),
            event_type='info_request',
            event_name='additional_info_requested',
            user=user,
            notes=f"Additional information requested: {info_request}",
            metadata={
                'info_request': info_request,
            }
        )

    def _extend_escalation_deadline(self, instance: Complaint, user, **kwargs):
        """Extend escalation deadline for info request"""
        from datetime import timedelta
        if instance.escalation_deadline:
            instance.escalation_deadline = instance.escalation_deadline + timedelta(days=3)
            instance.save(update_fields=['escalation_deadline'])

    def _notify_tenant_info_request(self, instance: Complaint, user, **kwargs):
        """Notify tenant of information request"""
        from .services import NotificationService
        if not instance.is_anonymous and instance.contact_preference != 'no_contact':
            NotificationService.create_notification(
                recipient=instance.tenant.user if hasattr(instance.tenant, 'user') else None,
                instance=instance,
                event='complaint_info_requested',
                config={
                    'title': 'Additional Information Needed',
                    'template': 'complaint_info_requested',
                    'priority': 'medium',
                },
                event_data=kwargs
            )

    def _set_resolution_date(self, instance: Complaint, user, **kwargs):
        """Set resolution date"""
        instance.resolution_date = timezone.now()
        instance.save(update_fields=['resolution_date'])

    def _log_resolution(self, instance: Complaint, user, **kwargs):
        """Log complaint resolution"""
        resolution = kwargs.get('resolution')
        from .services import AuditLogService
        AuditLogService.log_event(
            instance_type='Complaint',
            instance_id=str(instance.id),
            event_type='resolution',
            event_name='complaint_resolved',
            user=user,
            notes=f"Complaint resolved: {resolution[:100]}...",
            metadata={
                'resolution': resolution,
                'days_open': instance.days_open,
            }
        )

    def _notify_tenant_resolution(self, instance: Complaint, user, **kwargs):
        """Notify tenant of resolution"""
        from .services import NotificationService
        if not instance.is_anonymous and instance.contact_preference != 'no_contact':
            NotificationService.create_notification(
                recipient=instance.tenant.user if hasattr(instance.tenant, 'user') else None,
                instance=instance,
                event='complaint_resolved',
                config={
                    'title': 'Your Complaint Has Been Resolved',
                    'template': 'complaint_resolved',
                    'priority': 'medium',
                },
                event_data=kwargs
            )

    def _increase_priority(self, instance: Complaint, user, **kwargs):
        """Increase complaint priority on escalation"""
        priority_order = ['low', 'medium', 'high', 'urgent']
        try:
            current_index = priority_order.index(instance.priority)
            if current_index < len(priority_order) - 1:
                new_priority = priority_order[current_index + 1]
                instance.priority = new_priority
                instance.priority_changed = timezone.now()
                instance.save(update_fields=['priority', 'priority_changed'])
        except (ValueError, IndexError):
            pass  # Keep current priority if something goes wrong

    def _notify_management_escalation(self, instance: Complaint, user, **kwargs):
        """Notify management of escalation"""
        from .services import NotificationService
        NotificationService.create_notification(
            recipient=None,  # Notify all managers
            instance=instance,
            event='complaint_escalated',
            config={
                'title': 'Urgent: Complaint Escalated',
                'template': 'complaint_escalated',
                'priority': 'high',
            },
            event_data=kwargs
        )

    def _log_escalation(self, instance: Complaint, user, **kwargs):
        """Log complaint escalation"""
        from .services import AuditLogService
        AuditLogService.log_event(
            instance_type='Complaint',
            instance_id=str(instance.id),
            event_type='escalation',
            event_name='complaint_escalated',
            user=user,
            notes=f"Complaint escalated to {instance.priority} priority",
            metadata={
                'new_priority': instance.priority,
                'days_open': instance.days_open,
            }
        )

    def _log_closure(self, instance: Complaint, user, **kwargs):
        """Log complaint closure"""
        from .services import AuditLogService
        AuditLogService.log_event(
            instance_type='Complaint',
            instance_id=str(instance.id),
            event_type='closure',
            event_name='complaint_closed',
            user=user,
            notes=f"Complaint closed after {instance.days_open} days",
        )

    def _notify_tenant_closure(self, instance: Complaint, user, **kwargs):
        """Notify tenant of closure"""
        from .services import NotificationService
        if not instance.is_anonymous and instance.contact_preference != 'no_contact':
            NotificationService.create_notification(
                recipient=instance.tenant.user if hasattr(instance.tenant, 'user') else None,
                instance=instance,
                event='complaint_closed',
                config={
                    'title': 'Complaint Case Closed',
                    'template': 'complaint_closed',
                    'priority': 'low',
                },
                event_data={}
            )

    def _reset_escalation_deadline(self, instance: Complaint, user, **kwargs):
        """Reset escalation deadline on reopen"""
        self._set_escalation_deadline(instance, user, **kwargs)

    def _log_reopen(self, instance: Complaint, user, **kwargs):
        """Log complaint reopen"""
        reopen_reason = kwargs.get('reopen_reason', 'No reason provided')
        from .services import AuditLogService
        AuditLogService.log_event(
            instance_type='Complaint',
            instance_id=str(instance.id),
            event_type='reopen',
            event_name='complaint_reopened',
            user=user,
            notes=f"Complaint reopened: {reopen_reason}",
            metadata={
                'reopen_reason': reopen_reason,
            }
        )

    def _notify_staff_reopen(self, instance: Complaint, user, **kwargs):
        """Notify staff of reopen"""
        from .services import NotificationService
        NotificationService.create_notification(
            recipient=None,  # Notify all staff
            instance=instance,
            event='complaint_reopened',
            config={
                'title': 'Complaint Reopened',
                'template': 'complaint_reopened',
                'priority': 'medium',
            },
            event_data=kwargs
        )

    # Additional Workflow Methods

    def get_complaint_metrics(self) -> Dict[str, Any]:
        """Get complaint metrics for reporting"""
        return {
            'current_status': self.get_current_state(),
            'priority': self.instance.priority,
            'days_open': self.instance.days_open,
            'is_overdue': self.instance.is_overdue,
            'assigned_staff': self.instance.assigned_to.user.get_full_name() if self.instance.assigned_to else None,
            'escalation_deadline': self.instance.escalation_deadline.isoformat() if self.instance.escalation_deadline else None,
        }

    def get_complaint_history(self) -> List[Dict[str, Any]]:
        """Get complete complaint history"""
        from .services import AuditLogService
        return AuditLogService.get_events(
            instance_type='Complaint',
            instance_id=str(self.instance.id)
        )
