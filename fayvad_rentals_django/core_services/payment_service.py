"""
Payment Service - Pure Django Implementation
Manages payments with direct Django ORM
"""

from typing import Dict, List, Optional, Any
from decimal import Decimal
from django.db.models import Q, Sum
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from payments.models import Payment, PaymentStatus
import logging

User = get_user_model()

logger = logging.getLogger(__name__)


class PaymentService:
    """
    Pure Django service for payment operations
    """

    @staticmethod
    def get_payments(filters: Optional[Dict[str, Any]] = None, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """
        Get list of payments with filtering
        """
        try:
            queryset = Payment.objects.select_related(
                'tenant', 'rental_agreement', 'room'
            ).all()

            # Apply filters
            if filters:
                search = filters.get('search')
                if search:
                    queryset = queryset.filter(
                        Q(payment_number__icontains=search) |
                        Q(reference_number__icontains=search) |
                        Q(tenant__name__icontains=search)
                    )

                status = filters.get('status')
                if status:
                    queryset = queryset.filter(status=status)

                tenant_id = filters.get('tenant_id')
                if tenant_id:
                    queryset = queryset.filter(tenant_id=tenant_id)

                payment_method = filters.get('payment_method')
                if payment_method:
                    queryset = queryset.filter(payment_method=payment_method)

            # Paginate
            paginator = Paginator(queryset, page_size)
            page_obj = paginator.get_page(page)

            # Serialize
            payment_data = [
                {
                    'id': str(payment.id),
                    'payment_number': payment.payment_number,
                    'amount': float(payment.amount),
                    'payment_method': payment.payment_method,
                    'reference_number': payment.reference_number,
                    'status': payment.status,
                    'payment_date': payment.payment_date.isoformat() if payment.payment_date else None,
                    'tenant': {
                        'id': str(payment.tenant.id),
                        'name': payment.tenant.name
                    } if payment.tenant else None,
                    'rental_agreement': {
                        'id': str(payment.rental_agreement.id),
                        'agreement_number': payment.rental_agreement.agreement_number
                    } if payment.rental_agreement else None,
                    'is_completed': payment.is_completed,
                    'is_pending': payment.is_pending,
                }
                for payment in page_obj
            ]

            return {
                'success': True,
                'data': payment_data,
                'total': paginator.count,
                'page': page,
                'pages': paginator.num_pages,
            }

        except Exception as e:
            logger.error(f"Error getting payments: {e}")
            return {
                'success': False,
                'error': str(e),
                'data': []
            }

    @staticmethod
    def get_payment(payment_id: str) -> Dict[str, Any]:
        """
        Get single payment by ID
        """
        try:
            payment = Payment.objects.select_related(
                'tenant', 'rental_agreement', 'room'
            ).get(id=payment_id)

            payment_data = {
                'id': str(payment.id),
                'payment_number': payment.payment_number,
                'amount': float(payment.amount),
                'payment_method': payment.payment_method,
                'reference_number': payment.reference_number,
                'transaction_id': payment.transaction_id,
                'status': payment.status,
                'payment_date': payment.payment_date.isoformat() if payment.payment_date else None,
                'processed_date': payment.processed_date.isoformat() if payment.processed_date else None,
                'description': payment.description,
                'notes': payment.notes,
                'tenant': {
                    'id': str(payment.tenant.id),
                    'name': payment.tenant.name,
                    'email': payment.tenant.email,
                    'phone': payment.tenant.phone
                } if payment.tenant else None,
                'rental_agreement': {
                    'id': str(payment.rental_agreement.id),
                    'agreement_number': payment.rental_agreement.agreement_number
                } if payment.rental_agreement else None,
                'room': {
                    'id': str(payment.room.id),
                    'room_number': payment.room.room_number
                } if payment.room else None,
                'is_completed': payment.is_completed,
                'is_pending': payment.is_pending,
                'is_failed': payment.is_failed,
                'is_refundable': payment.is_refundable,
                'created_at': payment.created_at.isoformat(),
                'updated_at': payment.updated_at.isoformat(),
            }

            return {
                'success': True,
                'data': payment_data
            }

        except Payment.DoesNotExist:
            return {
                'success': False,
                'error': 'Payment not found'
            }
        except Exception as e:
            logger.error(f"Error getting payment {payment_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def create_payment(payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create new payment
        """
        try:
            from tenants.models import Tenant
            from rentals.models import RentalAgreement
            from properties.models import Room

            tenant = Tenant.objects.get(id=payment_data['tenant_id']) if payment_data.get('tenant_id') else None
            rental_agreement = RentalAgreement.objects.get(id=payment_data['rental_agreement_id']) if payment_data.get('rental_agreement_id') else None
            room = Room.objects.get(id=payment_data['room_id']) if payment_data.get('room_id') else None

            payment = Payment.objects.create(
                amount=payment_data['amount'],
                payment_method=payment_data.get('payment_method', 'mpesa'),
                reference_number=payment_data.get('reference_number'),
                tenant=tenant,
                rental_agreement=rental_agreement,
                room=room,
                payment_date=payment_data.get('payment_date'),
                description=payment_data.get('description'),
                notes=payment_data.get('notes'),
                status=payment_data.get('status', 'pending'),
            )

            return {
                'success': True,
                'data': {
                    'id': str(payment.id),
                    'payment_number': payment.payment_number,
                    'amount': float(payment.amount),
                    'status': payment.status,
                    'created_at': payment.created_at.isoformat(),
                },
                'message': 'Payment created successfully'
            }

        except Exception as e:
            logger.error(f"Error creating payment: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def complete_payment(payment_id: str, user: User, transaction_id: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Mark payment as completed using workflow engine (caretaker verification)
        """
        try:
            payment = Payment.objects.get(id=payment_id)

            # Use workflow engine
            from workflows import PaymentWorkflowEngine
            workflow = PaymentWorkflowEngine(payment)

            # Execute workflow transition with additional data
            transition_kwargs = {'transaction_id': transaction_id}
            transition_kwargs.update(kwargs)
            result = workflow.transition('verify_payment', user, **transition_kwargs)

            return {
                'success': True,
                'data': {
                    'id': str(payment.id),
                    'payment_number': payment.payment_number,
                    'status': payment.status,
                    'processed_date': payment.processed_date.isoformat() if payment.processed_date else None,
                    'workflow_history': workflow.get_workflow_history()[-1] if workflow.get_workflow_history() else None,
                },
                'message': result.get('message', 'Payment verified successfully')
            }

        except Payment.DoesNotExist:
            return {
                'success': False,
                'error': 'Payment not found'
            }
        except Exception as e:
            logger.error(f"Error verifying payment {payment_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def approve_payment(payment_id: str, user: User, transaction_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Approve payment using workflow engine (manager approval)
        """
        try:
            payment = Payment.objects.get(id=payment_id)

            # Use workflow engine
            from workflows import PaymentWorkflowEngine
            workflow = PaymentWorkflowEngine(payment)

            # Execute workflow transition
            result = workflow.transition('approve_payment', user, transaction_id=transaction_id)

            return {
                'success': True,
                'data': {
                    'id': str(payment.id),
                    'payment_number': payment.payment_number,
                    'status': payment.status,
                    'processed_date': payment.processed_date.isoformat() if payment.processed_date else None,
                    'workflow_history': workflow.get_workflow_history()[-1] if workflow.get_workflow_history() else None,
                },
                'message': result.get('message', 'Payment approved successfully')
            }

        except Payment.DoesNotExist:
            return {
                'success': False,
                'error': 'Payment not found'
            }
        except Exception as e:
            logger.error(f"Error approving payment {payment_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def get_workflow_status(payment_id: str, user: User) -> Dict[str, Any]:
        """
        Get workflow status for a payment
        """
        try:
            payment = Payment.objects.get(id=payment_id)

            # Get workflow information
            from workflows import PaymentWorkflowEngine
            workflow = PaymentWorkflowEngine(payment)

            return {
                'success': True,
                'data': {
                    'current_state': workflow.get_current_state(),
                    'available_events': workflow._get_available_events(user),
                    'verification_status': workflow.get_verification_status(),
                    'risk_score': workflow.get_payment_risk_score(),
                    'workflow_history': workflow.get_workflow_history(),
                    'workflow_metrics': workflow.get_workflow_metrics(),
                }
            }

        except Payment.DoesNotExist:
            return {
                'success': False,
                'error': 'Payment not found'
            }
        except Exception as e:
            logger.error(f"Error getting workflow status for payment {payment_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def fail_payment(payment_id: str, user: User, **kwargs) -> Dict[str, Any]:
        """
        Mark payment as failed using workflow engine (verification failed)
        """
        try:
            payment = Payment.objects.get(id=payment_id)

            # Use workflow engine
            from workflows import PaymentWorkflowEngine
            workflow = PaymentWorkflowEngine(payment)

            # Execute workflow transition with additional data
            result = workflow.transition('verify_payment_failed', user, **kwargs)

            return {
                'success': True,
                'data': {
                    'id': str(payment.id),
                    'payment_number': payment.payment_number,
                    'status': payment.status,
                }
            }

        except Payment.DoesNotExist:
            return {
                'success': False,
                'error': 'Payment not found'
            }
        except Exception as e:
            logger.error(f"Error failing payment {payment_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def get_tenant_payment_summary(tenant_id: str) -> Dict[str, Any]:
        """
        Get payment summary for a tenant
        """
        try:
            from tenants.models import Tenant
            tenant = Tenant.objects.get(id=tenant_id)

            completed_payments = Payment.objects.filter(
                tenant=tenant,
                status='completed'
            ).aggregate(
                total=Sum('amount'),
                count=Count('id')
            )

            pending_payments = Payment.objects.filter(
                tenant=tenant,
                status='pending'
            ).aggregate(
                total=Sum('amount'),
                count=Count('id')
            )

            summary = {
                'tenant_id': str(tenant.id),
                'tenant_name': tenant.name,
                'completed_payments': {
                    'total': float(completed_payments['total'] or 0),
                    'count': completed_payments['count']
                },
                'pending_payments': {
                    'total': float(pending_payments['total'] or 0),
                    'count': pending_payments['count']
                },
                'account_balance': float(tenant.account_balance),
            }

            return {
                'success': True,
                'data': summary
            }

        except Tenant.DoesNotExist:
            return {
                'success': False,
                'error': 'Tenant not found'
            }
        except Exception as e:
            logger.error(f"Error getting payment summary for tenant {tenant_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def reject_payment(payment_id: str, user: User, reason: str) -> Dict[str, Any]:
        """
        Reject payment using workflow engine
        """
        try:
            payment = Payment.objects.get(id=payment_id)

            # Use workflow engine
            from workflows import PaymentWorkflowEngine
            workflow = PaymentWorkflowEngine(payment)

            # Execute workflow transition
            result = workflow.transition('reject_payment', user, reason=reason)

            return {
                'success': True,
                'data': {
                    'id': str(payment.id),
                    'payment_number': payment.payment_number,
                    'status': payment.status,
                },
                'message': result.get('message', 'Payment rejected')
            }

        except Payment.DoesNotExist:
            return {
                'success': False,
                'error': 'Payment not found'
            }
        except Exception as e:
            logger.error(f"Error rejecting payment {payment_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def request_more_info(payment_id: str, user: User, message: str) -> Dict[str, Any]:
        """
        Request more information for payment verification
        """
        try:
            payment = Payment.objects.get(id=payment_id)

            # Use workflow engine
            from workflows import PaymentWorkflowEngine
            workflow = PaymentWorkflowEngine(payment)

            # Execute workflow transition
            result = workflow.transition('request_more_info', user, message=message)

            return {
                'success': True,
                'data': {
                    'id': str(payment.id),
                    'payment_number': payment.payment_number,
                    'status': payment.status,
                },
                'message': result.get('message', 'More information requested')
            }

        except Payment.DoesNotExist:
            return {
                'success': False,
                'error': 'Payment not found'
            }
        except Exception as e:
            logger.error(f"Error requesting more info for payment {payment_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def resubmit_payment(payment_id: str, user: User, **kwargs) -> Dict[str, Any]:
        """
        Resubmit payment for verification after providing more info
        """
        try:
            payment = Payment.objects.get(id=payment_id)

            # Use workflow engine
            from workflows import PaymentWorkflowEngine
            workflow = PaymentWorkflowEngine(payment)

            # Execute workflow transition
            result = workflow.transition('resubmit_payment', user, **kwargs)

            return {
                'success': True,
                'data': {
                    'id': str(payment.id),
                    'payment_number': payment.payment_number,
                    'status': payment.status,
                },
                'message': result.get('message', 'Payment resubmitted for verification')
            }

        except Payment.DoesNotExist:
            return {
                'success': False,
                'error': 'Payment not found'
            }
        except Exception as e:
            logger.error(f"Error resubmitting payment {payment_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def process_refund(payment_id: str, user: User, amount: Decimal, reason: str) -> Dict[str, Any]:
        """
        Process refund for payment
        """
        try:
            payment = Payment.objects.get(id=payment_id)

            # Use workflow engine
            from workflows import PaymentWorkflowEngine
            workflow = PaymentWorkflowEngine(payment)

            # Execute workflow transition
            result = workflow.transition('process_refund', user, amount=amount, reason=reason)

            return {
                'success': True,
                'data': {
                    'id': str(payment.id),
                    'payment_number': payment.payment_number,
                    'status': payment.status,
                },
                'message': result.get('message', 'Refund processed successfully')
            }

        except Payment.DoesNotExist:
            return {
                'success': False,
                'error': 'Payment not found'
            }
        except Exception as e:
            logger.error(f"Error processing refund for payment {payment_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def cancel_payment(payment_id: str, user: User, reason: str) -> Dict[str, Any]:
        """
        Cancel payment
        """
        try:
            payment = Payment.objects.get(id=payment_id)

            # Use workflow engine
            from workflows import PaymentWorkflowEngine
            workflow = PaymentWorkflowEngine(payment)

            # Execute workflow transition
            result = workflow.transition('cancel_payment', user, reason=reason)

            return {
                'success': True,
                'data': {
                    'id': str(payment.id),
                    'payment_number': payment.payment_number,
                    'status': payment.status,
                },
                'message': result.get('message', 'Payment cancelled')
            }

        except Payment.DoesNotExist:
            return {
                'success': False,
                'error': 'Payment not found'
            }
        except Exception as e:
            logger.error(f"Error cancelling payment {payment_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def mark_as_disputed(payment_id: str, user: User, reason: str) -> Dict[str, Any]:
        """
        Mark payment as disputed
        """
        try:
            payment = Payment.objects.get(id=payment_id)

            # Use workflow engine
            from workflows import PaymentWorkflowEngine
            workflow = PaymentWorkflowEngine(payment)

            # Execute workflow transition
            result = workflow.transition('mark_as_disputed', user, reason=reason)

            return {
                'success': True,
                'data': {
                    'id': str(payment.id),
                    'payment_number': payment.payment_number,
                    'status': payment.status,
                },
                'message': result.get('message', 'Payment marked as disputed')
            }

        except Payment.DoesNotExist:
            return {
                'success': False,
                'error': 'Payment not found'
            }
        except Exception as e:
            logger.error(f"Error marking payment as disputed {payment_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

