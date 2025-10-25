"""
Tenant Compliance and Violation Workflow Engine
Handles tenant compliance status, violations, and resolution workflows
"""

from typing import Dict, List, Any, Tuple, Optional
from django.core.exceptions import ValidationError
from django.utils import timezone
from .base import WorkflowEngine, WorkflowTransition, WorkflowTransitionError
from tenants.models import Tenant, ComplianceStatus

class TenantComplianceWorkflowEngine(WorkflowEngine):
    """
    Workflow engine for tenant compliance and violation management
    Handles status transitions and violation resolution processes
    """

    def _get_status_field(self) -> str:
        return 'compliance_status'

    def _define_transitions(self) -> Dict[str, WorkflowTransition]:
        """Define all possible tenant compliance workflow transitions"""

        return {
            'report_violation': WorkflowTransition(
                from_states=['compliant', 'warning'],
                to_state='violation',
                event='report_violation',
                required_permissions=['role:caretaker'],  # Staff can report violations
                validators=[
                    self._validate_violation_details,
                ],
                side_effects=[
                    self._log_violation,
                    self._schedule_follow_up,
                    self._send_violation_notice,
                ],
                description='Report a tenant violation'
            ),

            'issue_warning': WorkflowTransition(
                from_states=['compliant'],
                to_state='warning',
                event='issue_warning',
                required_permissions=['role:caretaker'],  # Staff can issue warnings
                validators=[
                    self._validate_warning_details,
                ],
                side_effects=[
                    self._log_warning,
                    self._schedule_warning_follow_up,
                    self._send_warning_notice,
                ],
                description='Issue a formal warning to tenant'
            ),

            'resolve_violation': WorkflowTransition(
                from_states=['violation', 'warning'],
                to_state='compliant',
                event='resolve_violation',
                required_permissions=['role:caretaker'],  # Staff can resolve violations
                validators=[
                    self._validate_resolution_details,
                ],
                side_effects=[
                    self._log_resolution,
                    self._clear_violation_history,
                    self._send_resolution_notice,
                ],
                description='Resolve violation and restore compliance'
            ),

            'escalate_violation': WorkflowTransition(
                from_states=['violation', 'warning'],
                to_state='violation',  # Status stays violation but escalated
                event='escalate_violation',
                required_permissions=['role:manager'],  # Only managers can escalate
                validators=[
                    self._validate_escalation_eligibility,
                ],
                side_effects=[
                    self._log_escalation,
                    self._schedule_urgent_action,
                    self._notify_management,
                ],
                description='Escalate violation to management'
            ),

            'blacklist_tenant': WorkflowTransition(
                from_states=['violation'],
                to_state='violation',  # Keep violation status but mark for blacklisting
                event='blacklist_tenant',
                required_permissions=['role:manager'],  # Only managers can blacklist
                validators=[
                    self._validate_blacklist_eligibility,
                ],
                side_effects=[
                    self._set_blacklisted_status,
                    self._terminate_agreements,
                    self._log_blacklisting,
                ],
                description='Blacklist tenant for severe violations'
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

        # Define role-based permissions for tenant compliance workflow
        event_permissions = {
            # Basic compliance actions - caretakers and above, or managers/superusers
            'report_violation': user_role in ['manager', 'caretaker'] or is_manager_or_superuser,
            'issue_warning': user_role in ['manager', 'caretaker'] or is_manager_or_superuser,
            'resolve_violation': user_role in ['manager', 'caretaker'] or is_manager_or_superuser,

            # Escalation actions - managers or superusers only
            'escalate_violation': user_role == 'manager' or is_manager_or_superuser,
            'blacklist_tenant': user_role == 'manager' or is_manager_or_superuser,
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

    def _validate_violation_details(self, instance: Tenant, user, **kwargs) -> Tuple[bool, str]:
        """Validate violation report details"""
        violation_type = kwargs.get('violation_type')
        description = kwargs.get('description')

        if not violation_type:
            return False, "Violation type is required"

        if not description or not description.strip():
            return False, "Violation description is required"

        if len(description.strip()) < 10:
            return False, "Violation description must be at least 10 characters"

        return True, "OK"

    def _validate_warning_details(self, instance: Tenant, user, **kwargs) -> Tuple[bool, str]:
        """Validate warning details"""
        warning_reason = kwargs.get('warning_reason')

        if not warning_reason or not warning_reason.strip():
            return False, "Warning reason is required"

        return True, "OK"

    def _validate_resolution_details(self, instance: Tenant, user, **kwargs) -> Tuple[bool, str]:
        """Validate violation resolution details"""
        resolution_notes = kwargs.get('resolution_notes')

        if not resolution_notes or not resolution_notes.strip():
            return False, "Resolution notes are required"

        return True, "OK"

    def _validate_escalation_eligibility(self, instance: Tenant, user, **kwargs) -> Tuple[bool, str]:
        """Validate if violation can be escalated"""
        # Check if tenant has been in violation status for more than 30 days
        if hasattr(instance, 'compliance_status_changed') and instance.compliance_status_changed:
            days_in_violation = (timezone.now().date() - instance.compliance_status_changed).days
            if days_in_violation < 30:
                return False, f"Violation must be active for at least 30 days before escalation (currently {days_in_violation} days)"

        return True, "OK"

    def _validate_blacklist_eligibility(self, instance: Tenant, user, **kwargs) -> Tuple[bool, str]:
        """Validate if tenant can be blacklisted"""
        # Check for multiple violations or severe violations
        if not hasattr(instance, 'violation_count') or instance.violation_count < 3:
            return False, "Tenant must have at least 3 violations before blacklisting"

        return True, "OK"

    # Side Effect Methods

    def _log_violation(self, instance: Tenant, user, **kwargs):
        """Log violation details"""
        violation_type = kwargs.get('violation_type')
        description = kwargs.get('description')

        from .services import AuditLogService
        AuditLogService.log_event(
            instance_type='Tenant',
            instance_id=str(instance.id),
            event_type='violation',
            event_name='violation_reported',
            user=user,
            notes=f"Violation reported: {violation_type} - {description}",
            metadata={
                'violation_type': violation_type,
                'description': description,
            }
        )

        # Update violation count
        if not hasattr(instance, 'violation_count'):
            instance.violation_count = 0
        instance.violation_count += 1
        instance.save(update_fields=['violation_count'])

    def _schedule_follow_up(self, instance: Tenant, user, **kwargs):
        """Schedule follow-up for violation"""
        # Schedule follow-up in 7 days
        from .services import NotificationService
        NotificationService.schedule_escalation(
            instance=instance,
            event_type='violation_follow_up',
            escalation_hours=168,  # 7 days
            priority='medium'
        )

    def _send_violation_notice(self, instance: Tenant, user, **kwargs):
        """Send violation notice to tenant"""
        from .services import NotificationService
        NotificationService.create_notification(
            recipient=instance.user if hasattr(instance, 'user') else None,
            instance=instance,
            event='violation_notice',
            config={
                'title': 'Compliance Violation Notice',
                'template': 'tenant_violation_notice',
                'priority': 'high',
            },
            event_data=kwargs
        )

    def _log_warning(self, instance: Tenant, user, **kwargs):
        """Log warning details"""
        warning_reason = kwargs.get('warning_reason')

        from .services import AuditLogService
        AuditLogService.log_event(
            instance_type='Tenant',
            instance_id=str(instance.id),
            event_type='warning',
            event_name='warning_issued',
            user=user,
            notes=f"Warning issued: {warning_reason}",
            metadata={
                'warning_reason': warning_reason,
            }
        )

    def _schedule_warning_follow_up(self, instance: Tenant, user, **kwargs):
        """Schedule warning follow-up"""
        from .services import NotificationService
        NotificationService.schedule_escalation(
            instance=instance,
            event_type='warning_follow_up',
            escalation_hours=72,  # 3 days
            priority='medium'
        )

    def _send_warning_notice(self, instance: Tenant, user, **kwargs):
        """Send warning notice to tenant"""
        from .services import NotificationService
        NotificationService.create_notification(
            recipient=instance.user if hasattr(instance, 'user') else None,
            instance=instance,
            event='warning_notice',
            config={
                'title': 'Formal Warning Notice',
                'template': 'tenant_warning_notice',
                'priority': 'medium',
            },
            event_data=kwargs
        )

    def _log_resolution(self, instance: Tenant, user, **kwargs):
        """Log violation resolution"""
        resolution_notes = kwargs.get('resolution_notes')

        from .services import AuditLogService
        AuditLogService.log_event(
            instance_type='Tenant',
            instance_id=str(instance.id),
            event_type='resolution',
            event_name='violation_resolved',
            user=user,
            notes=f"Violation resolved: {resolution_notes}",
            metadata={
                'resolution_notes': resolution_notes,
            }
        )

    def _clear_violation_history(self, instance: Tenant, user, **kwargs):
        """Clear violation history after resolution"""
        # Reset compliance status change date
        instance.compliance_status_changed = timezone.now().date()
        instance.save(update_fields=['compliance_status_changed'])

    def _send_resolution_notice(self, instance: Tenant, user, **kwargs):
        """Send resolution notice to tenant"""
        from .services import NotificationService
        NotificationService.create_notification(
            recipient=instance.user if hasattr(instance, 'user') else None,
            instance=instance,
            event='resolution_notice',
            config={
                'title': 'Compliance Resolution Notice',
                'template': 'tenant_resolution_notice',
                'priority': 'low',
            },
            event_data=kwargs
        )

    def _log_escalation(self, instance: Tenant, user, **kwargs):
        """Log violation escalation"""
        escalation_reason = kwargs.get('escalation_reason', 'Violation escalation')

        from .services import AuditLogService
        AuditLogService.log_event(
            instance_type='Tenant',
            instance_id=str(instance.id),
            event_type='escalation',
            event_name='violation_escalated',
            user=user,
            notes=f"Violation escalated: {escalation_reason}",
            metadata={
                'escalation_reason': escalation_reason,
            }
        )

    def _schedule_urgent_action(self, instance: Tenant, user, **kwargs):
        """Schedule urgent action for escalated violation"""
        from .services import NotificationService
        NotificationService.schedule_escalation(
            instance=instance,
            event_type='urgent_violation_action',
            escalation_hours=24,  # 1 day
            priority='urgent'
        )

    def _notify_management(self, instance: Tenant, user, **kwargs):
        """Notify management of escalated violation"""
        from .services import NotificationService
        NotificationService.create_notification(
            recipient=None,  # Send to all managers
            instance=instance,
            event='management_violation_alert',
            config={
                'title': 'Urgent: Escalated Tenant Violation',
                'template': 'management_violation_alert',
                'priority': 'urgent',
            },
            event_data=kwargs
        )

    def _set_blacklisted_status(self, instance: Tenant, user, **kwargs):
        """Set tenant status to blacklisted"""
        instance.status = 'blacklisted'
        instance.save(update_fields=['status'])

    def _terminate_agreements(self, instance: Tenant, user, **kwargs):
        """Terminate all active rental agreements"""
        from rentals.models import RentalAgreement
        active_agreements = RentalAgreement.objects.filter(
            tenant=instance,
            status='active'
        )

        for agreement in active_agreements:
            agreement.status = 'terminated'
            agreement.save()

    def _log_blacklisting(self, instance: Tenant, user, **kwargs):
        """Log tenant blacklisting"""
        blacklisting_reason = kwargs.get('blacklisting_reason', 'Severe violations')

        from .services import AuditLogService
        AuditLogService.log_event(
            instance_type='Tenant',
            instance_id=str(instance.id),
            event_type='blacklist',
            event_name='tenant_blacklisted',
            user=user,
            notes=f"Tenant blacklisted: {blacklisting_reason}",
            metadata={
                'blacklisting_reason': blacklisting_reason,
            }
        )

    # Additional Workflow Methods

    def get_compliance_history(self) -> List[Dict[str, Any]]:
        """Get complete compliance history for the tenant"""
        from .services import AuditLogService
        return AuditLogService.get_events(
            instance_type='Tenant',
            instance_id=str(self.instance.id)
        )

    def get_violation_metrics(self) -> Dict[str, Any]:
        """Get violation metrics for reporting"""
        return {
            'current_status': self.get_current_state(),
            'violation_count': getattr(self.instance, 'violation_count', 0),
            'days_in_current_status': self._calculate_days_in_status(),
            'compliance_history': self.get_compliance_history(),
        }

    def _calculate_days_in_status(self) -> int:
        """Calculate days in current compliance status"""
        if hasattr(self.instance, 'compliance_status_changed') and self.instance.compliance_status_changed:
            return (timezone.now().date() - self.instance.compliance_status_changed).days
        return 0
