"""
Rental Service - Pure Django Implementation
Manages rental agreements with direct Django ORM
"""

from typing import Dict, List, Optional, Any
from django.db.models import Q
from django.core.paginator import Paginator
from rentals.models import RentalAgreement, AgreementStatus
from properties.models import Room, RoomStatus
import logging

logger = logging.getLogger(__name__)


class RentalService:
    """
    Pure Django service for rental agreement operations
    """

    @staticmethod
    def get_rental_agreements(filters: Optional[Dict[str, Any]] = None, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """
        Get list of rental agreements with filtering
        """
        try:
            queryset = RentalAgreement.objects.select_related(
                'tenant', 'room', 'room__location'
            ).all()

            # Apply filters
            if filters:
                search = filters.get('search')
                if search:
                    queryset = queryset.filter(
                        Q(agreement_number__icontains=search) |
                        Q(tenant__name__icontains=search) |
                        Q(room__room_number__icontains=search)
                    )

                status = filters.get('status')
                if status:
                    queryset = queryset.filter(status=status)

                tenant_id = filters.get('tenant_id')
                if tenant_id:
                    queryset = queryset.filter(tenant_id=tenant_id)

                room_id = filters.get('room_id')
                if room_id:
                    queryset = queryset.filter(room_id=room_id)

            # Paginate
            paginator = Paginator(queryset, page_size)
            page_obj = paginator.get_page(page)

            # Serialize
            agreement_data = [
                {
                    'id': str(agreement.id),
                    'agreement_number': agreement.agreement_number,
                    'tenant': {
                        'id': str(agreement.tenant.id),
                        'name': agreement.tenant.name
                    },
                    'room': {
                        'id': str(agreement.room.id),
                        'room_number': agreement.room.room_number,
                        'location': agreement.room.location.name
                    },
                    'start_date': agreement.start_date.isoformat(),
                    'end_date': agreement.end_date.isoformat(),
                    'rent_amount': float(agreement.rent_amount),
                    'deposit_amount': float(agreement.deposit_amount),
                    'status': agreement.status,
                    'is_active': agreement.is_active,
                    'days_until_expiry': agreement.days_until_expiry,
                }
                for agreement in page_obj
            ]

            return {
                'success': True,
                'data': agreement_data,
                'total': paginator.count,
                'page': page,
                'pages': paginator.num_pages,
            }

        except Exception as e:
            logger.error(f"Error getting rental agreements: {e}")
            return {
                'success': False,
                'error': str(e),
                'data': []
            }

    @staticmethod
    def get_rental_agreement(agreement_id: str) -> Dict[str, Any]:
        """
        Get single rental agreement by ID
        """
        try:
            agreement = RentalAgreement.objects.select_related(
                'tenant', 'room', 'room__location'
            ).get(id=agreement_id)

            agreement_data = {
                'id': str(agreement.id),
                'agreement_number': agreement.agreement_number,
                'tenant': {
                    'id': str(agreement.tenant.id),
                    'name': agreement.tenant.name,
                    'email': agreement.tenant.email,
                    'phone': agreement.tenant.phone
                },
                'room': {
                    'id': str(agreement.room.id),
                    'room_number': agreement.room.room_number,
                    'location': {
                        'id': str(agreement.room.location.id),
                        'name': agreement.room.location.name,
                        'code': agreement.room.location.code
                    }
                },
                'start_date': agreement.start_date.isoformat(),
                'end_date': agreement.end_date.isoformat(),
                'rent_amount': float(agreement.rent_amount),
                'deposit_amount': float(agreement.deposit_amount),
                'status': agreement.status,
                'notice_given_date': agreement.notice_given_date.isoformat() if agreement.notice_given_date else None,
                'notice_period_days': agreement.notice_period_days,
                'special_terms': agreement.special_terms,
                'security_deposit_returned': agreement.security_deposit_returned,
                'security_deposit_return_date': agreement.security_deposit_return_date.isoformat() if agreement.security_deposit_return_date else None,
                'duration_days': agreement.duration_days,
                'duration_months': agreement.duration_months,
                'is_active': agreement.is_active,
                'is_expired': agreement.is_expired,
                'days_until_expiry': agreement.days_until_expiry,
                'outstanding_balance': agreement.outstanding_balance,
                'total_contract_value': agreement.total_contract_value,
                'can_be_terminated': agreement.can_be_terminated,
                'is_notice_period_active': agreement.is_notice_period_active,
                'created_at': agreement.created_at.isoformat(),
                'updated_at': agreement.updated_at.isoformat(),
            }

            return {
                'success': True,
                'data': agreement_data
            }

        except RentalAgreement.DoesNotExist:
            return {
                'success': False,
                'error': 'Rental agreement not found'
            }
        except Exception as e:
            logger.error(f"Error getting rental agreement {agreement_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def activate_agreement(agreement_id: str) -> Dict[str, Any]:
        """
        Activate a rental agreement
        """
        try:
            agreement = RentalAgreement.objects.select_related('tenant', 'room').get(id=agreement_id)

            if agreement.status != AgreementStatus.DRAFT:
                return {
                    'success': False,
                    'error': f'Can only activate draft agreements (current status: {agreement.status})'
                }

            # Activate agreement (this also updates room status)
            agreement.activate_agreement()

            # Update tenant status to active
            agreement.tenant.current_location = agreement.room.location
            agreement.tenant.tenant_status = 'active'
            agreement.tenant.save()

            return {
                'success': True,
                'data': {
                    'id': str(agreement.id),
                    'status': agreement.status,
                },
                'message': 'Rental agreement activated successfully'
            }

        except RentalAgreement.DoesNotExist:
            return {
                'success': False,
                'error': 'Rental agreement not found'
            }
        except Exception as e:
            logger.error(f"Error activating agreement {agreement_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def terminate_agreement(agreement_id: str, termination_date=None) -> Dict[str, Any]:
        """
        Terminate a rental agreement
        """
        try:
            agreement = RentalAgreement.objects.select_related('tenant', 'room').get(id=agreement_id)

            if not agreement.can_be_terminated:
                return {
                    'success': False,
                    'error': f'Cannot terminate agreement in {agreement.status} status'
                }

            # Terminate agreement (this also updates room status if no other active agreements)
            agreement.terminate_agreement(termination_date)

            # Check if tenant should become former (no other active agreements)
            from rentals.models import AgreementStatus
            other_active_agreements = RentalAgreement.objects.filter(
                tenant=agreement.tenant,
                status__in=[AgreementStatus.ACTIVE, AgreementStatus.DRAFT]
            ).exclude(pk=agreement.pk)

            # Update tenant
            agreement.tenant.current_location = None
            if not other_active_agreements.exists():
                agreement.tenant.tenant_status = 'former'
            agreement.tenant.save()

            return {
                'success': True,
                'data': {
                    'id': str(agreement.id),
                    'status': agreement.status,
                    'end_date': agreement.end_date.isoformat(),
                },
                'message': 'Rental agreement terminated successfully'
            }

        except RentalAgreement.DoesNotExist:
            return {
                'success': False,
                'error': 'Rental agreement not found'
            }
        except Exception as e:
            logger.error(f"Error terminating agreement {agreement_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

