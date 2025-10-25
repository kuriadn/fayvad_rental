"""
Rental Agreement Workflow Engine
Handles the complete tenant onboarding process from registration to active agreement
"""

from typing import Dict, List, Any, Tuple, Optional
from django.core.exceptions import ValidationError
from django.utils import timezone
from .base import WorkflowEngine, WorkflowTransition, WorkflowTransitionError
from rentals.models import RentalAgreement, AgreementStatus

class RentalAgreementWorkflowEngine(WorkflowEngine):
    """
    Workflow engine for rental agreement lifecycle
    Handles tenant registration → room allocation → agreement creation → activation
    """

    def _get_status_field(self) -> str:
        return 'status'

    def _define_transitions(self) -> Dict[str, WorkflowTransition]:
        """Define all possible rental agreement workflow transitions"""

        return {
            'create_draft_agreement': WorkflowTransition(
                from_states=[],  # Can create from any state (new agreement)
                to_state='draft',
                event='create_draft_agreement',
                required_permissions=['role:caretaker'],  # Staff can create draft agreements
                validators=[
                    self._validate_tenant_eligibility,
                    self._validate_room_availability,
                    self._validate_agreement_terms,
                ],
                side_effects=[
                    self._generate_agreement_number,
                    self._reserve_room,
                    self._log_agreement_creation,
                    self._notify_tenant_draft,
                ],
                description='Create draft rental agreement'
            ),

            'submit_for_tenant_review': WorkflowTransition(
                from_states=['draft'],
                to_state='draft',  # Status stays draft
                event='submit_for_tenant_review',
                required_permissions=['role:caretaker'],  # Staff submits for review
                validators=[
                    self._validate_agreement_completeness,
                ],
                side_effects=[
                    self._send_tenant_review_notification,
                    self._schedule_review_deadline,
                    self._log_review_submission,
                ],
                description='Submit agreement for tenant review'
            ),

            'tenant_approve_agreement': WorkflowTransition(
                from_states=['draft'],
                to_state='active',
                event='tenant_approve_agreement',
                required_permissions=[],  # Tenants can approve
                validators=[
                    self._validate_tenant_approval_eligibility,
                ],
                side_effects=[
                    self._activate_agreement,
                    self._update_room_status,
                    self._update_tenant_status,
                    self._schedule_rent_collection,
                    self._log_tenant_approval,
                    self._send_activation_notification,
                ],
                description='Tenant approves the rental agreement'
            ),

            'tenant_reject_agreement': WorkflowTransition(
                from_states=['draft'],
                to_state='draft',  # Status stays draft for revision
                event='tenant_reject_agreement',
                required_permissions=[],  # Tenants can reject
                validators=[
                    self._validate_rejection_reason,
                ],
                side_effects=[
                    self._log_tenant_rejection,
                    self._notify_staff_rejection,
                    self._schedule_revision_deadline,
                ],
                description='Tenant rejects the rental agreement'
            ),

            'staff_activate_agreement': WorkflowTransition(
                from_states=['draft'],
                to_state='active',
                event='staff_activate_agreement',
                required_permissions=['role:manager'],  # Managers can force activate
                validators=[
                    self._validate_activation_eligibility,
                ],
                side_effects=[
                    self._activate_agreement,
                    self._update_room_status,
                    self._update_tenant_status,
                    self._schedule_rent_collection,
                    self._log_staff_activation,
                    self._send_activation_notification,
                ],
                description='Staff activates agreement (override)'
            ),

            'revise_agreement': WorkflowTransition(
                from_states=['draft'],
                to_state='draft',  # Status stays draft
                event='revise_agreement',
                required_permissions=['role:caretaker'],  # Staff can revise
                validators=[
                    self._validate_revision_reason,
                ],
                side_effects=[
                    self._log_agreement_revision,
                    self._notify_tenant_revision,
                    self._extend_review_deadline,
                ],
                description='Revise agreement terms'
            ),

            'cancel_agreement': WorkflowTransition(
                from_states=['draft', 'active'],
                to_state='cancelled',
                event='cancel_agreement',
                required_permissions=['role:caretaker'],  # Staff can cancel
                validators=[
                    self._validate_cancellation_reason,
                ],
                side_effects=[
                    self._release_room_reservation,
                    self._log_cancellation,
                    self._notify_tenant_cancellation,
                ],
                description='Cancel the rental agreement'
            ),

            'terminate_agreement': WorkflowTransition(
                from_states=['active'],
                to_state='terminated',
                event='terminate_agreement',
                required_permissions=['role:manager'],  # Only managers can terminate
                validators=[
                    self._validate_termination_reason,
                ],
                side_effects=[
                    self._update_room_status_vacant,
                    self._update_tenant_status_former,
                    self._log_termination,
                    self._schedule_deposit_return,
                    self._notify_tenant_termination,
                ],
                description='Terminate active rental agreement'
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

        # Check if user is the tenant for this agreement
        is_agreement_tenant = (
            hasattr(self.instance, 'tenant') and
            self.instance.tenant and
            hasattr(self.instance.tenant, 'user') and
            self.instance.tenant.user == user
        )

        # Define role-based permissions for rental agreement workflow
        event_permissions = {
            # Staff actions - caretakers and above, or managers/superusers
            'create_draft_agreement': user_role in ['manager', 'caretaker'] or is_manager_or_superuser,
            'submit_for_tenant_review': user_role in ['manager', 'caretaker'] or is_manager_or_superuser,
            'revise_agreement': user_role in ['manager', 'caretaker'] or is_manager_or_superuser,
            'cancel_agreement': user_role in ['manager', 'caretaker'] or is_manager_or_superuser,
            'staff_activate_agreement': user_role == 'manager' or is_manager_or_superuser,
            'terminate_agreement': user_role == 'manager' or is_manager_or_superuser,

            # Tenant actions
            'tenant_approve_agreement': is_agreement_tenant,
            'tenant_reject_agreement': is_agreement_tenant,
        }

        # Check each transition - for UI display, only check permissions and state, not parameters
        for event, has_permission in event_permissions.items():
            if has_permission and event in self.transitions:
                transition = self.transitions[event]
                current_state = self.get_current_state()

                # Check if current state allows this transition
                if current_state in transition.from_states or (event == 'create_draft_agreement' and not self.instance.pk):
                    available_events.append(event)

        return available_events

    # Validation Methods

    def _validate_tenant_eligibility(self, instance: RentalAgreement, user, **kwargs) -> Tuple[bool, str]:
        """Validate tenant eligibility for agreement"""
        if not instance.tenant:
            return False, "Tenant is required"

        # Check tenant status
        if instance.tenant.status not in ['active', 'prospective']:
            return False, f"Tenant status '{instance.tenant.status}' does not allow new agreements"

        # Check compliance status
        if instance.tenant.compliance_status == 'violation':
            return False, "Tenant has active violations and cannot enter new agreements"

        return True, "OK"

    def _validate_room_availability(self, instance: RentalAgreement, user, **kwargs) -> Tuple[bool, str]:
        """Validate room availability"""
        if not instance.room:
            return False, "Room is required"

        if instance.room.status != 'vacant':
            return False, f"Room {instance.room.room_number} is not available (status: {instance.room.status})"

        return True, "OK"

    def _validate_agreement_terms(self, instance: RentalAgreement, user, **kwargs) -> Tuple[bool, str]:
        """Validate agreement terms"""
        if not instance.start_date or not instance.end_date:
            return False, "Agreement dates are required"

        if instance.start_date >= instance.end_date:
            return False, "End date must be after start date"

        if instance.start_date < timezone.now().date():
            return False, "Start date cannot be in the past"

        if not instance.rent_amount or instance.rent_amount <= 0:
            return False, "Valid rent amount is required"

        return True, "OK"

    def _validate_agreement_completeness(self, instance: RentalAgreement, user, **kwargs) -> Tuple[bool, str]:
        """Validate agreement is complete for tenant review"""
        required_fields = ['agreement_number', 'start_date', 'end_date', 'rent_amount', 'deposit_amount']

        for field in required_fields:
            if not getattr(instance, field):
                return False, f"Agreement is incomplete: {field} is required"

        return True, "OK"

    def _validate_tenant_approval_eligibility(self, instance: RentalAgreement, user, **kwargs) -> Tuple[bool, str]:
        """Validate tenant can approve agreement"""
        # Check if tenant has reviewed the agreement (this would be tracked separately)
        # For now, assume tenant can approve if they have access
        return True, "OK"

    def _validate_rejection_reason(self, instance: RentalAgreement, user, **kwargs) -> Tuple[bool, str]:
        """Validate rejection has a reason"""
        reason = kwargs.get('rejection_reason')
        if not reason or not reason.strip():
            return False, "Rejection reason is required"
        return True, "OK"

    def _validate_activation_eligibility(self, instance: RentalAgreement, user, **kwargs) -> Tuple[bool, str]:
        """Validate agreement can be activated"""
        if instance.status != 'draft':
            return False, "Only draft agreements can be activated"

        # Check all required conditions are met
        if not instance.agreement_number:
            return False, "Agreement number is required for activation"

        return True, "OK"

    def _validate_revision_reason(self, instance: RentalAgreement, user, **kwargs) -> Tuple[bool, str]:
        """Validate revision has a reason"""
        revision_reason = kwargs.get('revision_reason')
        if not revision_reason or not revision_reason.strip():
            return False, "Revision reason is required"
        return True, "OK"

    def _validate_cancellation_reason(self, instance: RentalAgreement, user, **kwargs) -> Tuple[bool, str]:
        """Validate cancellation has a reason"""
        reason = kwargs.get('cancellation_reason')
        if not reason or not reason.strip():
            return False, "Cancellation reason is required"
        return True, "OK"

    def _validate_termination_reason(self, instance: RentalAgreement, user, **kwargs) -> Tuple[bool, str]:
        """Validate termination has a reason"""
        reason = kwargs.get('termination_reason')
        if not reason or not reason.strip():
            return False, "Termination reason is required"
        return True, "OK"

    # Side Effect Methods

    def _generate_agreement_number(self, instance: RentalAgreement, user, **kwargs):
        """Generate unique agreement number"""
        if not instance.agreement_number:
            from django.utils import timezone
            timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
            instance.agreement_number = f"RA-{timestamp}-{str(instance.id)[:8]}"
            instance.save(update_fields=['agreement_number'])

    def _reserve_room(self, instance: RentalAgreement, user, **kwargs):
        """Reserve room for the agreement"""
        instance.room.status = 'reserved'
        instance.room.save(update_fields=['status'])

    def _log_agreement_creation(self, instance: RentalAgreement, user, **kwargs):
        """Log agreement creation"""
        from .services import AuditLogService
        AuditLogService.log_event(
            instance_type='RentalAgreement',
            instance_id=str(instance.id),
            event_type='creation',
            event_name='agreement_created',
            user=user,
            notes=f"Draft agreement created for tenant {instance.tenant.name} - Room {instance.room.room_number}",
            metadata={
                'tenant_id': str(instance.tenant.id),
                'room_id': str(instance.room.id),
                'rent_amount': float(instance.rent_amount),
            }
        )

    def _notify_tenant_draft(self, instance: RentalAgreement, user, **kwargs):
        """Notify tenant of draft agreement"""
        from .services import NotificationService
        NotificationService.create_notification(
            recipient=instance.tenant.user if hasattr(instance.tenant, 'user') else None,
            instance=instance,
            event='draft_agreement_ready',
            config={
                'title': 'Rental Agreement Ready for Review',
                'template': 'tenant_draft_agreement',
                'priority': 'medium',
            },
            event_data={}
        )

    def _send_tenant_review_notification(self, instance: RentalAgreement, user, **kwargs):
        """Send review notification to tenant"""
        from .services import NotificationService
        NotificationService.create_notification(
            recipient=instance.tenant.user if hasattr(instance.tenant, 'user') else None,
            instance=instance,
            event='agreement_review_request',
            config={
                'title': 'Please Review Your Rental Agreement',
                'template': 'tenant_agreement_review',
                'priority': 'high',
            },
            event_data={}
        )

    def _schedule_review_deadline(self, instance: RentalAgreement, user, **kwargs):
        """Schedule review deadline (7 days)"""
        from .services import NotificationService
        NotificationService.schedule_escalation(
            instance=instance,
            event_type='agreement_review_deadline',
            escalation_hours=168,  # 7 days
            priority='high'
        )

    def _log_review_submission(self, instance: RentalAgreement, user, **kwargs):
        """Log review submission"""
        from .services import AuditLogService
        AuditLogService.log_event(
            instance_type='RentalAgreement',
            instance_id=str(instance.id),
            event_type='review',
            event_name='submitted_for_review',
            user=user,
            notes=f"Agreement submitted for tenant review - {instance.tenant.name}",
        )

    def _activate_agreement(self, instance: RentalAgreement, user, **kwargs):
        """Activate the rental agreement"""
        instance.status = 'active'
        instance.save(update_fields=['status'])

    def _update_room_status(self, instance: RentalAgreement, user, **kwargs):
        """Update room status to occupied"""
        instance.room.status = 'occupied'
        instance.room.save(update_fields=['status'])

    def _update_tenant_status(self, instance: RentalAgreement, user, **kwargs):
        """Update tenant status to active"""
        instance.tenant.status = 'active'
        instance.tenant.save(update_fields=['status'])

    def _schedule_rent_collection(self, instance: RentalAgreement, user, **kwargs):
        """Schedule initial rent collection"""
        from .services import NotificationService
        NotificationService.schedule_escalation(
            instance=instance,
            event_type='initial_rent_due',
            escalation_hours=24,  # Next day
            priority='high'
        )

    def _log_tenant_approval(self, instance: RentalAgreement, user, **kwargs):
        """Log tenant approval"""
        from .services import AuditLogService
        AuditLogService.log_event(
            instance_type='RentalAgreement',
            instance_id=str(instance.id),
            event_type='approval',
            event_name='tenant_approved',
            user=user,
            notes=f"Tenant {instance.tenant.name} approved rental agreement",
        )

    def _send_activation_notification(self, instance: RentalAgreement, user, **kwargs):
        """Send activation notification"""
        from .services import NotificationService
        NotificationService.create_notification(
            recipient=instance.tenant.user if hasattr(instance.tenant, 'user') else None,
            instance=instance,
            event='agreement_activated',
            config={
                'title': 'Welcome! Your Rental Agreement is Active',
                'template': 'tenant_agreement_activated',
                'priority': 'high',
            },
            event_data={}
        )

    def _log_tenant_rejection(self, instance: RentalAgreement, user, **kwargs):
        """Log tenant rejection"""
        reason = kwargs.get('rejection_reason')
        from .services import AuditLogService
        AuditLogService.log_event(
            instance_type='RentalAgreement',
            instance_id=str(instance.id),
            event_type='rejection',
            event_name='tenant_rejected',
            user=user,
            notes=f"Tenant {instance.tenant.name} rejected agreement: {reason}",
            metadata={'rejection_reason': reason}
        )

    def _notify_staff_rejection(self, instance: RentalAgreement, user, **kwargs):
        """Notify staff of rejection"""
        from .services import NotificationService
        NotificationService.create_notification(
            recipient=None,  # Notify all staff
            instance=instance,
            event='agreement_rejected',
            config={
                'title': 'Rental Agreement Rejected by Tenant',
                'template': 'staff_agreement_rejected',
                'priority': 'high',
            },
            event_data=kwargs
        )

    def _schedule_revision_deadline(self, instance: RentalAgreement, user, **kwargs):
        """Schedule revision deadline"""
        from .services import NotificationService
        NotificationService.schedule_escalation(
            instance=instance,
            event_type='agreement_revision_deadline',
            escalation_hours=72,  # 3 days
            priority='medium'
        )

    def _log_staff_activation(self, instance: RentalAgreement, user, **kwargs):
        """Log staff activation"""
        from .services import AuditLogService
        AuditLogService.log_event(
            instance_type='RentalAgreement',
            instance_id=str(instance.id),
            event_type='activation',
            event_name='staff_activated',
            user=user,
            notes=f"Agreement activated by staff override for tenant {instance.tenant.name}",
        )

    def _log_agreement_revision(self, instance: RentalAgreement, user, **kwargs):
        """Log agreement revision"""
        reason = kwargs.get('revision_reason')
        from .services import AuditLogService
        AuditLogService.log_event(
            instance_type='RentalAgreement',
            instance_id=str(instance.id),
            event_type='revision',
            event_name='agreement_revised',
            user=user,
            notes=f"Agreement revised: {reason}",
            metadata={'revision_reason': reason}
        )

    def _notify_tenant_revision(self, instance: RentalAgreement, user, **kwargs):
        """Notify tenant of revision"""
        from .services import NotificationService
        NotificationService.create_notification(
            recipient=instance.tenant.user if hasattr(instance.tenant, 'user') else None,
            instance=instance,
            event='agreement_revised',
            config={
                'title': 'Rental Agreement Updated',
                'template': 'tenant_agreement_revised',
                'priority': 'medium',
            },
            event_data=kwargs
        )

    def _extend_review_deadline(self, instance: RentalAgreement, user, **kwargs):
        """Extend review deadline"""
        from .services import NotificationService
        NotificationService.schedule_escalation(
            instance=instance,
            event_type='agreement_review_deadline',
            escalation_hours=168,  # Reset to 7 days
            priority='high'
        )

    def _release_room_reservation(self, instance: RentalAgreement, user, **kwargs):
        """Release room reservation"""
        if instance.room.status == 'reserved':
            instance.room.status = 'vacant'
            instance.room.save(update_fields=['status'])

    def _log_cancellation(self, instance: RentalAgreement, user, **kwargs):
        """Log agreement cancellation"""
        reason = kwargs.get('cancellation_reason')
        from .services import AuditLogService
        AuditLogService.log_event(
            instance_type='RentalAgreement',
            instance_id=str(instance.id),
            event_type='cancellation',
            event_name='agreement_cancelled',
            user=user,
            notes=f"Agreement cancelled: {reason}",
            metadata={'cancellation_reason': reason}
        )

    def _notify_tenant_cancellation(self, instance: RentalAgreement, user, **kwargs):
        """Notify tenant of cancellation"""
        from .services import NotificationService
        NotificationService.create_notification(
            recipient=instance.tenant.user if hasattr(instance.tenant, 'user') else None,
            instance=instance,
            event='agreement_cancelled',
            config={
                'title': 'Rental Agreement Cancelled',
                'template': 'tenant_agreement_cancelled',
                'priority': 'high',
            },
            event_data=kwargs
        )

    def _update_room_status_vacant(self, instance: RentalAgreement, user, **kwargs):
        """Update room status to vacant"""
        instance.room.status = 'vacant'
        instance.room.save(update_fields=['status'])

    def _update_tenant_status_former(self, instance: RentalAgreement, user, **kwargs):
        """Update tenant status to former"""
        instance.tenant.status = 'former'
        instance.tenant.save(update_fields=['status'])

    def _log_termination(self, instance: RentalAgreement, user, **kwargs):
        """Log agreement termination"""
        reason = kwargs.get('termination_reason')
        from .services import AuditLogService
        AuditLogService.log_event(
            instance_type='RentalAgreement',
            instance_id=str(instance.id),
            event_type='termination',
            event_name='agreement_terminated',
            user=user,
            notes=f"Agreement terminated: {reason}",
            metadata={'termination_reason': reason}
        )

    def _schedule_deposit_return(self, instance: RentalAgreement, user, **kwargs):
        """Schedule deposit return process"""
        from .services import NotificationService
        NotificationService.schedule_escalation(
            instance=instance,
            event_type='deposit_return_due',
            escalation_hours=168,  # 7 days
            priority='medium'
        )

    def _notify_tenant_termination(self, instance: RentalAgreement, user, **kwargs):
        """Notify tenant of termination"""
        from .services import NotificationService
        NotificationService.create_notification(
            recipient=instance.tenant.user if hasattr(instance.tenant, 'user') else None,
            instance=instance,
            event='agreement_terminated',
            config={
                'title': 'Rental Agreement Terminated',
                'template': 'tenant_agreement_terminated',
                'priority': 'urgent',
            },
            event_data=kwargs
        )

    # Additional Workflow Methods

    def get_agreement_progress(self) -> Dict[str, Any]:
        """Get agreement creation progress"""
        return {
            'current_step': self._get_current_step(),
            'completed_steps': self._get_completed_steps(),
            'next_required_action': self._get_next_required_action(),
            'is_ready_for_activation': self._is_ready_for_activation(),
        }

    def _get_current_step(self) -> str:
        """Get current workflow step"""
        status = self.get_current_state()
        step_map = {
            'draft': 'draft_created',
            'active': 'activated',
            'cancelled': 'cancelled',
            'terminated': 'terminated',
        }
        return step_map.get(status, 'unknown')

    def _get_completed_steps(self) -> List[str]:
        """Get list of completed workflow steps"""
        steps = []
        if self.instance.agreement_number:
            steps.append('agreement_number_generated')
        if self.instance.start_date and self.instance.end_date:
            steps.append('dates_set')
        if self.instance.rent_amount > 0:
            steps.append('rent_amount_set')
        if self.instance.tenant and self.instance.tenant.status == 'active':
            steps.append('tenant_assigned')
        if self.instance.room and self.instance.room.status == 'occupied':
            steps.append('room_allocated')
        return steps

    def _get_next_required_action(self) -> str:
        """Get next required action"""
        if not self.instance.agreement_number:
            return 'generate_agreement_number'
        if not (self.instance.start_date and self.instance.end_date):
            return 'set_agreement_dates'
        if self.instance.rent_amount <= 0:
            return 'set_rent_amount'
        if not self.instance.tenant:
            return 'assign_tenant'
        if not self.instance.room:
            return 'allocate_room'
        if self.get_current_state() == 'draft':
            return 'submit_for_tenant_review'
        return 'agreement_complete'

    def _is_ready_for_activation(self) -> bool:
        """Check if agreement is ready for activation"""
        return (
            self.instance.agreement_number and
            self.instance.start_date and
            self.instance.end_date and
            self.instance.rent_amount > 0 and
            self.instance.tenant and
            self.instance.room and
            self.get_current_state() == 'draft'
        )
