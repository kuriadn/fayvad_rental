"""
Workflow API Views
REST endpoints for workflow management
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
import json

from core_services.maintenance_service import MaintenanceService
from core_services.payment_service import PaymentService
from core_services.tenant_service import TenantService
from core_services.rental_service import RentalService
from core_services.complaint_service import ComplaintService
from ..services import AuditLogService, NotificationService


@login_required
@require_http_methods(["GET"])
def get_workflow_status(request, instance_type, instance_id):
    """
    Get workflow status for any instance
    GET /api/workflows/{instance_type}/{instance_id}/status/
    """
    try:
        if instance_type == 'maintenance':
            result = MaintenanceService.get_workflow_status(instance_id, request.user)
        elif instance_type == 'payment':
            result = PaymentService.get_workflow_status(instance_id, request.user)
        elif instance_type == 'tenant':
            result = TenantService.get_workflow_status(instance_id, request.user)
        elif instance_type == 'rental':
            result = RentalService.get_workflow_status(instance_id, request.user)
        elif instance_type == 'complaint':
            result = ComplaintService.get_workflow_status(instance_id, request.user)
        else:
            return JsonResponse({
                'success': False,
                'error': f'Unknown instance type: {instance_type}'
            }, status=400)

        if result['success']:
            return JsonResponse(result)
        else:
            return JsonResponse(result, status=404)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def perform_workflow_action(request, instance_type, instance_id):
    """
    Perform a workflow action
    POST /api/workflows/{instance_type}/{instance_id}/action/
    Body: {"action": "assign_technician", "data": {...}}
    """
    try:
        # Parse request body
        try:
            body = json.loads(request.body)
            action = body.get('action')
            action_data = body.get('data', {})
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON body'
            }, status=400)

        if not action:
            return JsonResponse({
                'success': False,
                'error': 'Action parameter is required'
            }, status=400)

        # Route to appropriate service
        if instance_type == 'maintenance':
            result = _perform_maintenance_action(instance_id, action, action_data, request.user)
        elif instance_type == 'payment':
            result = _perform_payment_action(instance_id, action, action_data, request.user)
        elif instance_type == 'tenant':
            result = _perform_tenant_action(instance_id, action, action_data, request.user)
        elif instance_type == 'rental':
            result = _perform_rental_action(instance_id, action, action_data, request.user)
        elif instance_type == 'complaint':
            result = _perform_complaint_action(instance_id, action, action_data, request.user)
        else:
            return JsonResponse({
                'success': False,
                'error': f'Unknown instance type: {instance_type}'
            }, status=400)

        # Send notifications for successful actions
        if result.get('success'):
            _send_workflow_notifications(instance_type, instance_id, action, request.user, action_data)

        return JsonResponse(result)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def _perform_maintenance_action(instance_id, action, action_data, user):
    """Handle maintenance workflow actions"""
    try:
        if action == 'assign_technician':
            technician_name = action_data.get('technician_name')
            if not technician_name:
                raise ValidationError('technician_name is required')
            return MaintenanceService.assign_technician(instance_id, technician_name, user)

        elif action == 'complete_request':
            resolution_notes = action_data.get('resolution_notes')
            actual_cost = action_data.get('actual_cost')
            return MaintenanceService.complete_request(instance_id, user, resolution_notes, actual_cost)

        elif action == 'cancel_request':
            reason = action_data.get('reason')
            if not reason:
                raise ValidationError('Cancellation reason is required')
            return MaintenanceService.cancel_request(instance_id, user, reason)

        elif action == 'reopen_request':
            reason = action_data.get('reason', 'Reopened by user')
            return MaintenanceService.reopen_request(instance_id, user, reason)

        elif action == 'escalate_priority':
            new_priority = action_data.get('new_priority')
            if not new_priority or new_priority not in ['high', 'urgent']:
                raise ValidationError('Valid priority (high or urgent) is required')
            return MaintenanceService.escalate_priority(instance_id, user, new_priority)

        elif action == 'schedule_maintenance':
            scheduled_date = action_data.get('scheduled_date')
            if not scheduled_date:
                raise ValidationError('Scheduled date is required')
            return MaintenanceService.schedule_maintenance(instance_id, user, scheduled_date)

        elif action == 'start_work':
            work_notes = action_data.get('work_notes', '')
            return MaintenanceService.start_work(instance_id, user, work_notes)

        else:
            return {
                'success': False,
                'error': f'Unknown maintenance action: {action}'
            }

    except ValidationError as e:
        return {
            'success': False,
            'error': str(e)
        }


def _perform_payment_action(instance_id, action, action_data, user):
    """Handle payment workflow actions"""
    try:
        transaction_id = action_data.get('transaction_id')

        if action == 'submit_for_verification':
            submission_notes = action_data.get('submission_notes', '')
            # Use the workflow engine directly since we don't have a service method
            from workflows import PaymentWorkflowEngine
            from payments.models import Payment
            payment = Payment.objects.get(id=instance_id)
            workflow = PaymentWorkflowEngine(payment)
            result = workflow.transition('submit_for_verification', user, notes=submission_notes)
            return {
                'success': result.get('success', False),
                'message': result.get('message', 'Payment submitted for verification'),
                'data': {
                    'id': str(payment.id),
                    'status': payment.status,
                    'new_state': payment.status
                }
            }

        elif action == 'verify_payment_completed':
            return PaymentService.complete_payment(instance_id, user, transaction_id, **action_data)

        elif action == 'verify_payment_failed':
            return PaymentService.fail_payment(instance_id, user, **action_data)

        elif action == 'approve_payment':
            return PaymentService.approve_payment(instance_id, user, transaction_id)

        elif action == 'reject_payment':
            reason = action_data.get('reason', 'No reason provided')
            return PaymentService.reject_payment(instance_id, user, reason)

        elif action == 'request_more_info':
            message = action_data.get('message', 'Please provide more information')
            return PaymentService.request_more_info(instance_id, user, message)

        elif action == 'resubmit_payment':
            return PaymentService.resubmit_payment(instance_id, user, **action_data)

        elif action == 'process_refund':
            from decimal import Decimal
            amount = Decimal(str(action_data.get('amount', 0)))
            reason = action_data.get('reason', 'Refund requested')
            return PaymentService.process_refund(instance_id, user, amount, reason)

        elif action == 'cancel_payment':
            reason = action_data.get('reason', 'Payment cancelled')
            return PaymentService.cancel_payment(instance_id, user, reason)

        elif action == 'mark_as_disputed':
            reason = action_data.get('reason', 'Payment disputed')
            return PaymentService.mark_as_disputed(instance_id, user, reason)

        else:
            return {
                'success': False,
                'error': f'Unknown payment action: {action}'
            }

    except ValidationError as e:
        return {
            'success': False,
            'error': str(e)
        }


def _perform_tenant_action(instance_id, action, action_data, user):
    """Handle tenant compliance workflow actions"""
    try:
        from tenants.models import Tenant
        tenant = Tenant.objects.get(id=instance_id)

        if action == 'report_violation':
            violation_type = action_data.get('violation_type')
            description = action_data.get('description')
            if not violation_type or not description:
                raise ValidationError('Violation type and description are required')

            from workflows.tenant import TenantComplianceWorkflowEngine
            workflow = TenantComplianceWorkflowEngine(tenant)
            result = workflow.transition('report_violation', user,
                                       violation_type=violation_type,
                                       description=description)
            return {
                'success': result.get('success', False),
                'message': result.get('message', 'Violation reported successfully'),
                'data': {
                    'id': str(tenant.id),
                    'compliance_status': tenant.compliance_status,
                }
            }

        elif action == 'issue_warning':
            warning_reason = action_data.get('warning_reason')
            if not warning_reason:
                raise ValidationError('Warning reason is required')

            from workflows.tenant import TenantComplianceWorkflowEngine
            workflow = TenantComplianceWorkflowEngine(tenant)
            result = workflow.transition('issue_warning', user,
                                       warning_reason=warning_reason)
            return {
                'success': result.get('success', False),
                'message': result.get('message', 'Warning issued successfully'),
                'data': {
                    'id': str(tenant.id),
                    'compliance_status': tenant.compliance_status,
                }
            }

        elif action == 'resolve_violation':
            resolution_notes = action_data.get('resolution_notes')
            if not resolution_notes:
                raise ValidationError('Resolution notes are required')

            from workflows.tenant import TenantComplianceWorkflowEngine
            workflow = TenantComplianceWorkflowEngine(tenant)
            result = workflow.transition('resolve_violation', user,
                                       resolution_notes=resolution_notes)
            return {
                'success': result.get('success', False),
                'message': result.get('message', 'Violation resolved successfully'),
                'data': {
                    'id': str(tenant.id),
                    'compliance_status': tenant.compliance_status,
                }
            }

        elif action == 'escalate_violation':
            escalation_reason = action_data.get('escalation_reason', 'Violation escalation')

            from workflows.tenant import TenantComplianceWorkflowEngine
            workflow = TenantComplianceWorkflowEngine(tenant)
            result = workflow.transition('escalate_violation', user,
                                       escalation_reason=escalation_reason)
            return {
                'success': result.get('success', False),
                'message': result.get('message', 'Violation escalated successfully'),
                'data': {
                    'id': str(tenant.id),
                    'compliance_status': tenant.compliance_status,
                }
            }

        elif action == 'blacklist_tenant':
            blacklisting_reason = action_data.get('blacklisting_reason', 'Severe violations')

            from workflows.tenant import TenantComplianceWorkflowEngine
            workflow = TenantComplianceWorkflowEngine(tenant)
            result = workflow.transition('blacklist_tenant', user,
                                       blacklisting_reason=blacklisting_reason)
            return {
                'success': result.get('success', False),
                'message': result.get('message', 'Tenant blacklisted successfully'),
                'data': {
                    'id': str(tenant.id),
                    'status': tenant.status,
                    'compliance_status': tenant.compliance_status,
                }
            }

        else:
            return {
                'success': False,
                'error': f'Unknown tenant action: {action}'
            }

    except ValidationError as e:
        return {
            'success': False,
            'error': str(e)
        }


def _perform_rental_action(instance_id, action, action_data, user):
    """Handle rental agreement workflow actions"""
    try:
        from rentals.models import RentalAgreement
        agreement = RentalAgreement.objects.get(id=instance_id)

        if action == 'create_draft_agreement':
            # This is typically done through the regular create view, but we can handle it here too
            from workflows.rental import RentalAgreementWorkflowEngine
            workflow = RentalAgreementWorkflowEngine(agreement)
            result = workflow.transition('create_draft_agreement', user)
            return {
                'success': result.get('success', False),
                'message': result.get('message', 'Draft agreement created successfully'),
                'data': {
                    'id': str(agreement.id),
                    'status': agreement.status,
                    'agreement_number': agreement.agreement_number,
                }
            }

        elif action == 'submit_for_tenant_review':
            from workflows.rental import RentalAgreementWorkflowEngine
            workflow = RentalAgreementWorkflowEngine(agreement)
            result = workflow.transition('submit_for_tenant_review', user)
            return {
                'success': result.get('success', False),
                'message': result.get('message', 'Agreement submitted for tenant review'),
                'data': {
                    'id': str(agreement.id),
                    'status': agreement.status,
                }
            }

        elif action == 'tenant_approve_agreement':
            from workflows.rental import RentalAgreementWorkflowEngine
            workflow = RentalAgreementWorkflowEngine(agreement)
            result = workflow.transition('tenant_approve_agreement', user)
            return {
                'success': result.get('success', False),
                'message': result.get('message', 'Agreement approved successfully'),
                'data': {
                    'id': str(agreement.id),
                    'status': agreement.status,
                }
            }

        elif action == 'tenant_reject_agreement':
            rejection_reason = action_data.get('rejection_reason')
            if not rejection_reason:
                raise ValidationError('Rejection reason is required')

            from workflows.rental import RentalAgreementWorkflowEngine
            workflow = RentalAgreementWorkflowEngine(agreement)
            result = workflow.transition('tenant_reject_agreement', user,
                                       rejection_reason=rejection_reason)
            return {
                'success': result.get('success', False),
                'message': result.get('message', 'Agreement rejected'),
                'data': {
                    'id': str(agreement.id),
                    'status': agreement.status,
                }
            }

        elif action == 'staff_activate_agreement':
            from workflows.rental import RentalAgreementWorkflowEngine
            workflow = RentalAgreementWorkflowEngine(agreement)
            result = workflow.transition('staff_activate_agreement', user)
            return {
                'success': result.get('success', False),
                'message': result.get('message', 'Agreement activated by staff'),
                'data': {
                    'id': str(agreement.id),
                    'status': agreement.status,
                }
            }

        elif action == 'revise_agreement':
            revision_reason = action_data.get('revision_reason')
            if not revision_reason:
                raise ValidationError('Revision reason is required')

            from workflows.rental import RentalAgreementWorkflowEngine
            workflow = RentalAgreementWorkflowEngine(agreement)
            result = workflow.transition('revise_agreement', user,
                                       revision_reason=revision_reason)
            return {
                'success': result.get('success', False),
                'message': result.get('message', 'Agreement revised successfully'),
                'data': {
                    'id': str(agreement.id),
                    'status': agreement.status,
                }
            }

        elif action == 'cancel_agreement':
            cancellation_reason = action_data.get('cancellation_reason')
            if not cancellation_reason:
                raise ValidationError('Cancellation reason is required')

            from workflows.rental import RentalAgreementWorkflowEngine
            workflow = RentalAgreementWorkflowEngine(agreement)
            result = workflow.transition('cancel_agreement', user,
                                       cancellation_reason=cancellation_reason)
            return {
                'success': result.get('success', False),
                'message': result.get('message', 'Agreement cancelled successfully'),
                'data': {
                    'id': str(agreement.id),
                    'status': agreement.status,
                }
            }

        elif action == 'terminate_agreement':
            termination_reason = action_data.get('termination_reason')
            if not termination_reason:
                raise ValidationError('Termination reason is required')

            from workflows.rental import RentalAgreementWorkflowEngine
            workflow = RentalAgreementWorkflowEngine(agreement)
            result = workflow.transition('terminate_agreement', user,
                                       termination_reason=termination_reason)
            return {
                'success': result.get('success', False),
                'message': result.get('message', 'Agreement terminated successfully'),
                'data': {
                    'id': str(agreement.id),
                    'status': agreement.status,
                }
            }

        else:
            return {
                'success': False,
                'error': f'Unknown rental action: {action}'
            }

    except ValidationError as e:
        return {
            'success': False,
            'error': str(e)
        }


def _perform_complaint_action(instance_id, action, action_data, user):
    """Handle complaint workflow actions"""
    try:
        from tenants.models import Complaint
        complaint = Complaint.objects.get(id=instance_id)

        if action == 'submit_complaint':
            # This is typically done through the create view, but we can handle it here too
            from workflows.complaint import ComplaintWorkflowEngine
            workflow = ComplaintWorkflowEngine(complaint)
            result = workflow.transition('submit_complaint', user)
            return {
                'success': result.get('success', False),
                'message': result.get('message', 'Complaint submitted successfully'),
                'data': {
                    'id': str(complaint.id),
                    'complaint_number': complaint.complaint_number,
                    'status': complaint.status,
                }
            }

        elif action == 'assign_investigator':
            assignee_id = action_data.get('assignee_id')
            if not assignee_id:
                raise ValidationError('Assignee is required')

            from workflows.complaint import ComplaintWorkflowEngine
            workflow = ComplaintWorkflowEngine(complaint)
            result = workflow.transition('assign_investigator', user,
                                       assignee_id=assignee_id)
            return {
                'success': result.get('success', False),
                'message': result.get('message', 'Investigator assigned successfully'),
                'data': {
                    'id': str(complaint.id),
                    'status': complaint.status,
                    'assigned_to': complaint.assigned_to.user.get_full_name() if complaint.assigned_to else None,
                }
            }

        elif action == 'update_priority':
            new_priority = action_data.get('new_priority')
            if not new_priority or new_priority not in ['low', 'medium', 'high', 'urgent']:
                raise ValidationError('Valid priority level is required')

            from workflows.complaint import ComplaintWorkflowEngine
            workflow = ComplaintWorkflowEngine(complaint)
            result = workflow.transition('update_priority', user,
                                       new_priority=new_priority)
            return {
                'success': result.get('success', False),
                'message': result.get('message', 'Priority updated successfully'),
                'data': {
                    'id': str(complaint.id),
                    'priority': complaint.priority,
                }
            }

        elif action == 'request_more_info':
            info_request = action_data.get('info_request')
            if not info_request:
                raise ValidationError('Information request details are required')

            from workflows.complaint import ComplaintWorkflowEngine
            workflow = ComplaintWorkflowEngine(complaint)
            result = workflow.transition('request_more_info', user,
                                       info_request=info_request)
            return {
                'success': result.get('success', False),
                'message': result.get('message', 'Information requested from tenant'),
                'data': {
                    'id': str(complaint.id),
                    'status': complaint.status,
                }
            }

        elif action == 'resolve_complaint':
            resolution = action_data.get('resolution')
            if not resolution:
                raise ValidationError('Resolution details are required')

            from workflows.complaint import ComplaintWorkflowEngine
            workflow = ComplaintWorkflowEngine(complaint)
            result = workflow.transition('resolve_complaint', user,
                                       resolution=resolution)
            return {
                'success': result.get('success', False),
                'message': result.get('message', 'Complaint resolved successfully'),
                'data': {
                    'id': str(complaint.id),
                    'status': complaint.status,
                    'resolution': complaint.resolution,
                }
            }

        elif action == 'escalate_complaint':
            escalation_reason = action_data.get('escalation_reason', 'Complaint escalation')

            from workflows.complaint import ComplaintWorkflowEngine
            workflow = ComplaintWorkflowEngine(complaint)
            result = workflow.transition('escalate_complaint', user,
                                       escalation_reason=escalation_reason)
            return {
                'success': result.get('success', False),
                'message': result.get('message', 'Complaint escalated successfully'),
                'data': {
                    'id': str(complaint.id),
                    'priority': complaint.priority,
                    'status': complaint.status,
                }
            }

        elif action == 'close_complaint':
            from workflows.complaint import ComplaintWorkflowEngine
            workflow = ComplaintWorkflowEngine(complaint)
            result = workflow.transition('close_complaint', user)
            return {
                'success': result.get('success', False),
                'message': result.get('message', 'Complaint closed successfully'),
                'data': {
                    'id': str(complaint.id),
                    'status': complaint.status,
                }
            }

        elif action == 'reopen_complaint':
            reopen_reason = action_data.get('reopen_reason', 'Complaint reopened')

            from workflows.complaint import ComplaintWorkflowEngine
            workflow = ComplaintWorkflowEngine(complaint)
            result = workflow.transition('reopen_complaint', user,
                                       reopen_reason=reopen_reason)
            return {
                'success': result.get('success', False),
                'message': result.get('message', 'Complaint reopened successfully'),
                'data': {
                    'id': str(complaint.id),
                    'status': complaint.status,
                }
            }

        else:
            return {
                'success': False,
                'error': f'Unknown complaint action: {action}'
            }

    except ValidationError as e:
        return {
            'success': False,
            'error': str(e)
        }


@login_required
@require_http_methods(["GET"])
def get_workflow_history(request, instance_type, instance_id):
    """
    Get workflow history for an instance
    GET /api/workflows/{instance_type}/{instance_id}/history/
    """
    try:
        history = AuditLogService.get_workflow_history(instance_type.title(), instance_id)

        return JsonResponse({
            'success': True,
            'data': history
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_user_notifications(request):
    """
    Get workflow notifications for current user
    GET /api/workflows/notifications/
    """
    try:
        unread_only = request.GET.get('unread_only', 'false').lower() == 'true'
        notifications = NotificationService.get_user_notifications(request.user, unread_only)

        return JsonResponse({
            'success': True,
            'data': notifications
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def mark_notifications_read(request):
    """
    Mark notifications as read
    POST /api/workflows/notifications/mark-read/
    Body: {"notification_ids": [1, 2, 3]}
    """
    try:
        try:
            body = json.loads(request.body)
            notification_ids = body.get('notification_ids', [])
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON body'
            }, status=400)

        NotificationService.mark_notifications_read(request.user, notification_ids)

        return JsonResponse({
            'success': True,
            'message': f'Marked {len(notification_ids)} notifications as read'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_workflow_audit_summary(request):
    """
    Get workflow audit summary
    GET /api/workflows/audit/summary/
    """
    try:
        days = int(request.GET.get('days', 30))
        summary = AuditLogService.get_audit_summary(days=days)

        return JsonResponse({
            'success': True,
            'data': summary
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def _send_workflow_notifications(instance_type, instance_id, action, user, action_data):
    """Send workflow notifications for successful actions"""
    try:
        # Get the instance
        if instance_type == 'maintenance':
            from maintenance.models import MaintenanceRequest
            instance = MaintenanceRequest.objects.get(id=instance_id)
        elif instance_type == 'payment':
            from payments.models import Payment
            instance = Payment.objects.get(id=instance_id)
        else:
            return

        # Send notifications
        NotificationService.notify_workflow_transition(
            instance=instance,
            event=action,
            user=user,
            **action_data
        )

    except Exception as e:
        # Don't break the main flow if notifications fail
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to send workflow notifications: {e}")
