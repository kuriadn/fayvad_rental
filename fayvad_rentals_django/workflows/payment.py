"""
Payment Workflow Engine
Handles payment verification, approval, and processing workflows
"""

from typing import Dict, List, Any, Tuple, Optional
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.utils import timezone
from .base import WorkflowEngine, WorkflowTransition, WorkflowTransitionError
from payments.models import Payment, PaymentStatus, PaymentMethod


class PaymentWorkflowEngine(WorkflowEngine):
    """
    Workflow engine for payment processing
    Handles verification, approval, and rejection workflows
    """

    def _get_status_field(self) -> str:
        return 'status'

    def _define_transitions(self) -> Dict[str, WorkflowTransition]:
        """Define all possible payment workflow transitions"""

        return {
            'submit_for_verification': WorkflowTransition(
                from_states=['pending'],
                to_state='pending',  # Status stays pending, but marked for verification
                event='submit_for_verification',
                required_permissions=[],  # Tenants can submit
                validators=[
                    self._validate_payment_data,
                    self._validate_amount_limits,
                ],
                side_effects=[
                    self._flag_for_verification,
                    self._schedule_verification_reminder,
                ],
                description='Submit payment for staff verification'
            ),

            'verify_payment_completed': WorkflowTransition(
                from_states=['pending'],
                to_state='completed',
                event='verify_payment_completed',
                required_permissions=['role:caretaker'],  # Caretakers can verify
                validators=[
                    self._validate_verification_data,
                    self._validate_payment_proof,
                    self._validate_amount_matches,
                ],
                side_effects=[
                    self._set_payment_date,
                    self._set_processed_date,
                    self._update_tenant_balance,
                    self._generate_receipt,
                ],
                description='Verify payment as completed'
            ),

            'verify_payment_failed': WorkflowTransition(
                from_states=['pending'],
                to_state='failed',
                event='verify_payment_failed',
                required_permissions=['role:caretaker'],  # Caretakers can verify
                validators=[
                    self._validate_verification_data,
                ],
                side_effects=[
                    self._log_verification_failure,
                ],
                description='Verify payment as failed'
            ),

            'approve_payment': WorkflowTransition(
                from_states=['pending'],
                to_state='completed',
                event='approve_payment',
                required_permissions=['role:manager'],  # Only managers can approve
                validators=[
                    self._validate_verification_data,
                    self._validate_payment_proof,
                    self._validate_amount_matches,
                ],
                side_effects=[
                    self._set_processed_date,
                    self._update_tenant_balance,
                    self._generate_receipt,
                ],
                description='Approve the payment (managers only)'
            ),

            'reject_payment': WorkflowTransition(
                from_states=['pending'],
                to_state='failed',
                event='reject_payment',
                required_permissions=['role:caretaker'],  # Caretakers and managers can reject
                validators=[
                    self._validate_rejection_reason,
                ],
                side_effects=[
                    self._log_rejection_reason,
                    self._notify_tenant_of_rejection,
                ],
                description='Reject the payment with reason'
            ),

            'request_more_info': WorkflowTransition(
                from_states=['pending', 'failed'],
                to_state='pending',
                event='request_more_info',
                required_permissions=['role:caretaker'],  # Caretakers and managers can request info
                validators=[
                    self._validate_info_request,
                ],
                side_effects=[
                    self._send_info_request_notification,
                    self._set_info_deadline,
                ],
                description='Request additional information from tenant'
            ),

            'resubmit_payment': WorkflowTransition(
                from_states=['failed'],
                to_state='pending',
                event='resubmit_payment',
                required_permissions=[],  # Tenants can resubmit
                validators=[
                    self._validate_resubmission_eligibility,
                    self._validate_updated_data,
                ],
                side_effects=[
                    self._reset_verification_flags,
                    self._log_resubmission,
                ],
                description='Resubmit payment with corrections'
            ),

            'process_refund': WorkflowTransition(
                from_states=['completed'],
                to_state='refunded',
                event='process_refund',
                required_permissions=['role:manager'],  # Only managers can process refunds
                validators=[
                    self._validate_refund_eligibility,
                    self._validate_refund_amount,
                ],
                side_effects=[
                    self._process_refund_transaction,
                    self._update_tenant_balance,
                    self._generate_refund_receipt,
                ],
                description='Process a refund for the payment'
            ),

            'cancel_payment': WorkflowTransition(
                from_states=['pending'],
                to_state='cancelled',
                event='cancel_payment',
                required_permissions=['role:manager'],  # Only managers can cancel payments
                validators=[
                    self._validate_cancellation_reason,
                ],
                side_effects=[
                    self._log_cancellation,
                ],
                description='Cancel the payment'
            ),

            'mark_as_disputed': WorkflowTransition(
                from_states=['completed', 'failed'],
                to_state='completed',  # Status stays the same, but marked as disputed
                event='mark_as_disputed',
                required_permissions=['role:manager'],  # Only managers can mark as disputed
                validators=[],
                side_effects=[
                    self._flag_as_disputed,
                    self._notify_dispute_team,
                ],
                description='Mark payment as disputed for investigation'
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

        # Check user role
        try:
            staff_profile = user.staff_profile
            user_role = staff_profile.role if staff_profile and staff_profile.is_active_staff else None
        except AttributeError:
            user_role = None

        # Check if user is tenant owner
        is_tenant_owner = (
            hasattr(self.instance, 'tenant') and
            self.instance.tenant and
            hasattr(self.instance.tenant, 'user') and
            self.instance.tenant.user == user
        )

        # Define role-based permissions for payment workflow
        event_permissions = {
            # Tenant actions
            'submit_for_verification': is_tenant_owner and not user_role,
            'resubmit_payment': is_tenant_owner and not user_role,

            # Caretaker actions (can verify but not approve), or managers/superusers
            'verify_payment_completed': user_role in ['caretaker'] or is_manager_or_superuser,
            'verify_payment_failed': user_role in ['caretaker'] or is_manager_or_superuser,
            'reject_payment': user_role in ['caretaker'] or is_manager_or_superuser,
            'request_more_info': user_role in ['caretaker'] or is_manager_or_superuser,

            # Manager actions (can validate AND approve), or superusers
            'approve_payment': user_role == 'manager' or is_manager_or_superuser,
            'process_refund': user_role == 'manager' or is_manager_or_superuser,
            'cancel_payment': user_role == 'manager' or is_manager_or_superuser,
            'mark_as_disputed': user_role == 'manager' or is_manager_or_superuser,
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

    def _validate_payment_data(self, instance: Payment, user, **kwargs) -> Tuple[bool, str]:
        """Validate basic payment data"""
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"DEBUG: _validate_payment_data called for instance {instance.id}, payment_date: {instance.payment_date}")

        if not instance.amount or instance.amount <= 0:
            return False, "Payment amount must be greater than zero"

        if not instance.payment_method:
            return False, "Payment method is required"

        if instance.payment_method in [PaymentMethod.MPESA, PaymentMethod.BANK_TRANSFER]:
            if not instance.reference_number:
                return False, f"Reference number is required for {instance.payment_method}"

        if not instance.payment_date:
            logger.error(f"DEBUG: Payment date validation failed for instance {instance.id}")
            return False, "Payment date is required"

        return True, "OK"

    def _validate_amount_limits(self, instance: Payment, user, **kwargs) -> Tuple[bool, str]:
        """Validate payment amount limits"""
        # Define reasonable limits to prevent fraud
        max_amount = Decimal('500000.00')  # 500k max
        min_amount = Decimal('1.00')       # 1 min

        if instance.amount > max_amount:
            return False, f"Payment amount cannot exceed {max_amount}"

        if instance.amount < min_amount:
            return False, f"Payment amount must be at least {min_amount}"

        return True, "OK"

    def _validate_verification_data(self, instance: Payment, user, **kwargs) -> Tuple[bool, str]:
        """Validate data required for verification"""
        # Staff must provide verification notes or transaction ID
        verification_notes = kwargs.get('verification_notes')
        if verification_notes:
            # Set verification notes on the instance
            instance.notes = verification_notes
        elif not hasattr(instance, 'processor_response') or not instance.processor_response:
            if not instance.notes:
                return False, "Verification notes are required"

        return True, "OK"

    def _validate_payment_proof(self, instance: Payment, user, **kwargs) -> Tuple[bool, str]:
        """Validate payment proof is available"""
        # For M-Pesa and bank transfers, we need some form of verification
        if instance.payment_method in [PaymentMethod.MPESA, PaymentMethod.BANK_TRANSFER]:
            has_reference = bool(instance.reference_number)
            has_transaction_id = bool(instance.transaction_id)
            has_notes = bool(instance.notes and len(instance.notes.strip()) > 10)

            if not (has_reference or has_transaction_id or has_notes):
                return False, "Payment proof required (reference number, transaction ID, or verification notes)"

        return True, "OK"

    def _validate_amount_matches(self, instance: Payment, user, **kwargs) -> Tuple[bool, str]:
        """Validate payment amount matches expected amount"""
        # This could check against expected rent amount for the period
        # For now, just ensure amount is reasonable
        if instance.amount > Decimal('100000.00'):  # Flag large amounts for manual review
            return False, "Large payment amounts require additional verification"

        return True, "OK"

    def _validate_rejection_reason(self, instance: Payment, user, **kwargs) -> Tuple[bool, str]:
        """Validate rejection has a proper reason"""
        reason = kwargs.get('reason')
        if not reason or not reason.strip():
            return False, "Rejection reason is required"
        return True, "OK"

    def _validate_info_request(self, instance: Payment, user, **kwargs) -> Tuple[bool, str]:
        """Validate information request"""
        return True, "OK"

    def _validate_resubmission_eligibility(self, instance: Payment, user, **kwargs) -> Tuple[bool, str]:
        """Validate payment can be resubmitted"""
        # Allow resubmission within 30 days of rejection
        if instance.status != PaymentStatus.FAILED:
            return False, "Only failed payments can be resubmitted"

        if hasattr(instance, 'updated_at'):
            days_since_failure = (timezone.now() - instance.updated_at).days
            if days_since_failure > 30:
                return False, "Payments can only be resubmitted within 30 days of rejection"

        return True, "OK"

    def _validate_updated_data(self, instance: Payment, user, **kwargs) -> Tuple[bool, str]:
        """Validate that data has been updated for resubmission"""
        # Check if any relevant fields have been updated
        return True, "OK"

    def _validate_refund_eligibility(self, instance: Payment, user, **kwargs) -> Tuple[bool, str]:
        """Validate payment can be refunded"""
        if instance.status != PaymentStatus.COMPLETED:
            return False, "Only completed payments can be refunded"

        # Check time limit (e.g., within 90 days)
        if hasattr(instance, 'processed_date') and instance.processed_date:
            days_since_payment = (timezone.now() - instance.processed_date).days
            if days_since_payment > 90:
                return False, "Refunds can only be processed within 90 days of payment"

        return True, "OK"

    def _validate_refund_amount(self, instance: Payment, user, **kwargs) -> Tuple[bool, str]:
        """Validate refund amount"""
        refund_amount = kwargs.get('refund_amount')
        if refund_amount is not None:
            if refund_amount <= 0:
                return False, "Refund amount must be greater than zero"
            if refund_amount > instance.amount:
                return False, "Refund amount cannot exceed payment amount"
        return True, "OK"

    def _validate_cancellation_reason(self, instance: Payment, user, **kwargs) -> Tuple[bool, str]:
        """Validate cancellation has a reason"""
        reason = kwargs.get('reason')
        if not reason or not reason.strip():
            return False, "Cancellation reason is required"
        return True, "OK"

    # Side Effect Methods

    def _flag_for_verification(self, instance: Payment, user, **kwargs):
        """Flag payment for staff verification"""
        instance.notes = (instance.notes or "") + "\n[Submitted for verification]"
        instance.save(update_fields=['notes'])

    def _schedule_verification_reminder(self, instance: Payment, user, **kwargs):
        """Schedule reminder for staff to verify payment"""
        from .services import NotificationService

        # Schedule reminder in 24 hours if not verified
        NotificationService.schedule_escalation(
            instance=instance,
            event_type='payment_verification_pending',
            escalation_hours=24,
            priority='medium'
        )

    def _set_payment_date(self, instance: Payment, user, **kwargs):
        """Set payment date from verification form"""
        import logging
        logger = logging.getLogger(__name__)

        payment_date_str = kwargs.get('payment_date')
        logger.error(f"DEBUG: _set_payment_date called with payment_date_str: {payment_date_str}, kwargs: {kwargs}")

        if payment_date_str:
            from django.utils.dateparse import parse_datetime
            payment_date = parse_datetime(payment_date_str)
            logger.error(f"DEBUG: parsed payment_date: {payment_date}")
            if payment_date:
                instance.payment_date = payment_date.date()
                instance.save(update_fields=['payment_date'])
                logger.error(f"DEBUG: payment_date set to: {instance.payment_date}")
            else:
                logger.error(f"DEBUG: Failed to parse payment_date_str: {payment_date_str}")
        else:
            logger.error("DEBUG: No payment_date_str provided")

    def _set_processed_date(self, instance: Payment, user, **kwargs):
        """Set payment processed date"""
        instance.processed_date = timezone.now()
        instance.save(update_fields=['processed_date'])

    def _log_verification_failure(self, instance: Payment, user, **kwargs):
        """Log verification failure reason"""
        from .services import AuditLogService

        reason = kwargs.get('verification_notes', 'Verification failed - no reason provided')
        AuditLogService.log_event(
            instance_type='payment',
            instance_id=str(instance.id),
            event_type='verification_failed',
            user=user,
            details={
                'reason': reason,
                'payment_amount': float(instance.amount),
                'tenant': str(instance.tenant) if instance.tenant else None
            }
        )

    def _update_tenant_balance(self, instance: Payment, user, **kwargs):
        """Update tenant account balance"""
        if hasattr(instance, 'tenant') and instance.tenant:
            # For completed payments, add to balance
            # For refunds, subtract from balance
            if instance.status == PaymentStatus.COMPLETED:
                instance.tenant.account_balance += instance.amount
            elif instance.status == PaymentStatus.REFUNDED:
                refund_amount = kwargs.get('refund_amount', instance.amount)
                instance.tenant.account_balance -= refund_amount

            instance.tenant.save(update_fields=['account_balance'])

    def _generate_receipt(self, instance: Payment, user, **kwargs):
        """Generate payment receipt"""
        # This could trigger PDF generation or email receipt
        from .services import AuditLogService

        AuditLogService.log_event(
            instance_type='Payment',
            instance_id=str(instance.id),
            event_type='manual',
            event_name='receipt_generated',
            user=user,
            notes=f"Payment receipt generated for {instance.payment_number}",
        )

    def _log_rejection_reason(self, instance: Payment, user, **kwargs):
        """Log payment rejection with reason"""
        reason = kwargs.get('reason', 'No reason provided')

        instance.processor_response = f"Rejected: {reason}"
        instance.save(update_fields=['processor_response'])

        from .services import AuditLogService

        AuditLogService.log_event(
            instance_type='Payment',
            instance_id=str(instance.id),
            event_type='validation',
            event_name='payment_rejected',
            user=user,
            notes=f"Payment rejected: {reason}",
            metadata={'rejection_reason': reason}
        )

    def _notify_tenant_of_rejection(self, instance: Payment, user, **kwargs):
        """Notify tenant of payment rejection"""
        # This will be handled by the notification service post-transition
        pass

    def _send_info_request_notification(self, instance: Payment, user, **kwargs):
        """Send information request to tenant"""
        from .services import NotificationService

        # Create notification for tenant
        if hasattr(instance, 'tenant') and instance.tenant and hasattr(instance.tenant, 'user'):
            NotificationService._create_notification(
                recipient=instance.tenant.user,
                instance=instance,
                event='info_requested',
                config={
                    'title': 'Additional Information Required',
                    'template': 'payment_info_request',
                    'priority': 'medium',
                },
                event_data=kwargs
            )

    def _set_info_deadline(self, instance: Payment, user, **kwargs):
        """Set deadline for providing additional information"""
        # Could set a deadline field on the payment
        pass

    def _reset_verification_flags(self, instance: Payment, user, **kwargs):
        """Reset verification flags for resubmission"""
        instance.processor_response = ""
        instance.notes = (instance.notes or "").replace("[Submitted for verification]", "").strip()
        instance.save(update_fields=['processor_response', 'notes'])

    def _log_resubmission(self, instance: Payment, user, **kwargs):
        """Log payment resubmission"""
        from .services import AuditLogService

        AuditLogService.log_event(
            instance_type='Payment',
            instance_id=str(instance.id),
            event_type='manual',
            event_name='payment_resubmitted',
            user=user,
            notes="Payment resubmitted with corrections",
        )

    def _process_refund_transaction(self, instance: Payment, user, **kwargs):
        """Process refund transaction"""
        refund_amount = kwargs.get('refund_amount', instance.amount)

        # This would integrate with payment processor for actual refund
        from .services import AuditLogService

        AuditLogService.log_event(
            instance_type='Payment',
            instance_id=str(instance.id),
            event_type='manual',
            event_name='refund_processed',
            user=user,
            notes=f"Refund processed: {refund_amount}",
            metadata={'refund_amount': str(refund_amount)}
        )

    def _generate_refund_receipt(self, instance: Payment, user, **kwargs):
        """Generate refund receipt"""
        from .services import AuditLogService

        AuditLogService.log_event(
            instance_type='Payment',
            instance_id=str(instance.id),
            event_type='manual',
            event_name='refund_receipt_generated',
            user=user,
            notes="Refund receipt generated",
        )

    def _log_cancellation(self, instance: Payment, user, **kwargs):
        """Log payment cancellation"""
        reason = kwargs.get('reason', 'No reason provided')
        from .services import AuditLogService

        AuditLogService.log_event(
            instance_type='Payment',
            instance_id=str(instance.id),
            event_type='manual',
            event_name='payment_cancelled',
            user=user,
            notes=f"Payment cancelled: {reason}",
            metadata={'cancellation_reason': reason}
        )

    def _flag_as_disputed(self, instance: Payment, user, **kwargs):
        """Flag payment as disputed"""
        instance.notes = (instance.notes or "") + "\n[DISPUTED - Under investigation]"
        instance.save(update_fields=['notes'])

    def _notify_dispute_team(self, instance: Payment, user, **kwargs):
        """Notify dispute resolution team"""
        from .services import NotificationService

        # This would notify a specific dispute team group
        NotificationService.schedule_escalation(
            instance=instance,
            event_type='payment_dispute',
            escalation_hours=4,
            priority='high'
        )

    # Additional Payment Workflow Methods

    def get_verification_status(self) -> Dict[str, Any]:
        """Get verification status and requirements"""
        if self.instance.status == PaymentStatus.COMPLETED:
            return {
                'status': 'verified',
                'verified_by': getattr(self.instance, 'updated_by', None),
                'verified_at': self.instance.processed_date,
                'transaction_id': self.instance.transaction_id,
            }
        elif self.instance.status == PaymentStatus.FAILED:
            return {
                'status': 'rejected',
                'rejected_reason': self.instance.processor_response,
                'can_resubmit': self._can_resubmit(),
            }
        else:
            return {
                'status': 'pending_verification',
                'submitted_days_ago': self._days_since_submission(),
                'requires_attention': self._requires_attention(),
            }

    def _can_resubmit(self) -> bool:
        """Check if payment can be resubmitted"""
        try:
            can_transition, _ = self.can_transition('resubmit_payment', self.instance.tenant.user)
            return can_transition
        except:
            return False

    def _days_since_submission(self) -> int:
        """Calculate days since payment was submitted"""
        if hasattr(self.instance, 'created_at'):
            return (timezone.now() - self.instance.created_at).days
        return 0

    def _requires_attention(self) -> bool:
        """Check if payment requires immediate attention"""
        days_pending = self._days_since_submission()

        # Large amounts need quick verification
        if self.instance.amount > Decimal('50000.00'):
            return days_pending > 1

        # Urgent payments (marked in notes)
        if self.instance.notes and 'urgent' in self.instance.notes.lower():
            return days_pending > 0

        # Normal payments
        return days_pending > 3

    def get_payment_risk_score(self) -> Dict[str, Any]:
        """Calculate risk score for payment verification"""
        score = 0
        factors = []

        # Amount-based risk
        if self.instance.amount > Decimal('100000.00'):
            score += 3
            factors.append('high_amount')
        elif self.instance.amount > Decimal('25000.00'):
            score += 2
            factors.append('medium_amount')

        # Payment method risk
        if self.instance.payment_method == PaymentMethod.CASH:
            score += 2
            factors.append('cash_payment')
        elif self.instance.payment_method == PaymentMethod.OTHER:
            score += 1
            factors.append('unusual_method')

        # Missing verification data
        if not self.instance.reference_number:
            score += 1
            factors.append('no_reference')

        # First-time large payment
        if self._is_first_large_payment():
            score += 1
            factors.append('first_large_payment')

        risk_level = 'low' if score <= 2 else 'medium' if score <= 4 else 'high'

        return {
            'score': score,
            'level': risk_level,
            'factors': factors,
            'requires_additional_review': score >= 3,
        }

    def _is_first_large_payment(self) -> bool:
        """Check if this is the tenant's first large payment"""
        if not hasattr(self.instance, 'tenant') or not self.instance.tenant:
            return False

        large_threshold = Decimal('10000.00')
        previous_large_payments = Payment.objects.filter(
            tenant=self.instance.tenant,
            amount__gte=large_threshold,
            status=PaymentStatus.COMPLETED
        ).exclude(id=self.instance.id).exists()

        return not previous_large_payments

    def get_workflow_metrics(self) -> Dict[str, Any]:
        """Get workflow metrics for reporting"""
        return {
            'current_state': self.get_current_state(),
            'days_pending': self._days_since_submission(),
            'verification_status': self.get_verification_status(),
            'risk_score': self.get_payment_risk_score(),
            'total_transitions': len(self.get_workflow_history()),
        }
