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
    def create_rental_agreement(agreement_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create new rental agreement
        """
        try:
            from tenants.models import Tenant

            tenant = Tenant.objects.get(id=agreement_data['tenant_id'])
            room = Room.objects.get(id=agreement_data['room_id'])

            # Validate room is available
            if room.status != RoomStatus.AVAILABLE:
                return {
                    'success': False,
                    'error': f'Room is not available (current status: {room.status})'
                }

            # Create agreement
            agreement = RentalAgreement.objects.create(
                tenant=tenant,
                room=room,
                start_date=agreement_data['start_date'],
                end_date=agreement_data['end_date'],
                rent_amount=agreement_data['rent_amount'],
                deposit_amount=agreement_data.get('deposit_amount', 0),
                status=agreement_data.get('status', 'draft'),
                special_terms=agreement_data.get('special_terms'),
                notice_period_days=agreement_data.get('notice_period_days', 30),
            )

            # Update room status if agreement is active
            if agreement.status == 'active':
                room.status = RoomStatus.OCCUPIED
                room.save()

                # Update tenant location
                tenant.current_location = room.location
                tenant.tenant_status = 'active'
                tenant.save()

            return {
                'success': True,
                'data': {
                    'id': str(agreement.id),
                    'agreement_number': agreement.agreement_number,
                    'tenant_name': tenant.name,
                    'room_number': room.room_number,
                    'status': agreement.status,
                    'created_at': agreement.created_at.isoformat(),
                },
                'message': 'Rental agreement created successfully'
            }

        except (Tenant.DoesNotExist, Room.DoesNotExist) as e:
            return {
                'success': False,
                'error': str(e)
            }
        except Exception as e:
            logger.error(f"Error creating rental agreement: {e}")
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

            # Activate agreement
            agreement.activate_agreement()

            # Update room status
            agreement.room.status = RoomStatus.OCCUPIED
            agreement.room.save()

            # Update tenant
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

            # Terminate agreement
            agreement.terminate_agreement(termination_date)

            # Update room status
            agreement.room.status = RoomStatus.AVAILABLE
            agreement.room.save()

            # Update tenant
            agreement.tenant.current_location = None
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

    @staticmethod
    def get_workflow_status(agreement_id: str, user) -> Dict[str, Any]:
        """
        Get workflow status for rental agreement
        """
        try:
            agreement = RentalAgreement.objects.get(id=agreement_id)

            # Use the rental agreement workflow engine
            from workflows.rental import RentalAgreementWorkflowEngine
            workflow = RentalAgreementWorkflowEngine(agreement)

            # Get current state and available events
            current_state = workflow.get_current_state()
            available_events = workflow._get_available_events(user)

            # Get workflow history
            from workflows.services import AuditLogService
            workflow_history = AuditLogService.get_workflow_history('RentalAgreement', agreement_id)

            # Get agreement progress
            agreement_progress = workflow.get_agreement_progress()

            return {
                'success': True,
                'data': {
                    'current_state': current_state,
                    'available_events': available_events,
                    'workflow_history': workflow_history,
                    'agreement_status': agreement.status,
                    'agreement_number': agreement.agreement_number,
                    'tenant_name': agreement.tenant.name if agreement.tenant else None,
                    'room_info': f"{agreement.room.room_number} ({agreement.room.location.name})" if agreement.room else None,
                    'progress': agreement_progress,
                    'is_ready_for_activation': agreement_progress.get('is_ready_for_activation', False),
                }
            }

        except RentalAgreement.DoesNotExist:
            return {
                'success': False,
                'error': 'Rental agreement not found'
            }
        except Exception as e:
            logger.error(f"Error getting rental agreement workflow status {agreement_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

