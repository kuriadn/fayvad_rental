"""
Payment Service - Pure Django Implementation
Manages payments with direct Django ORM
"""

from typing import Dict, List, Optional, Any
from django.db.models import Q, Sum
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from payments.models import Payment
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
        Mark payment as completed
        """
        try:
            payment = Payment.objects.get(id=payment_id)

            # Update payment fields directly
            from django.utils import timezone
            payment.processed_date = timezone.now()
            if transaction_id:
                payment.transaction_id = transaction_id

            # Change status to completed
            from .workflow_service import SimpleWorkflowService
            workflow_result = SimpleWorkflowService.transition_state(
                payment, 'completed', user
            )
            if not workflow_result['success']:
                return {
                    'success': False,
                    'error': workflow_result['error']
                }

            payment.save()

            return {
                'success': True,
                'data': {
                    'id': str(payment.id),
                    'payment_number': payment.payment_number,
                    'status': payment.status,
                    'processed_date': payment.processed_date.isoformat() if payment.processed_date else None,
                },
                'message': 'Payment completed successfully'
            }

        except Payment.DoesNotExist:
            return {
                'success': False,
                'error': 'Payment not found'
            }
        except Exception as e:
            logger.error(f"Error completing payment {payment_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
