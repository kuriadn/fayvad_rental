"""
Tenant Service - Pure Django Implementation
Replaces FBS async tenant operations with direct Django ORM
"""

from typing import Dict, List, Optional, Any
from django.db.models import Q, Count, Sum
from django.core.paginator import Paginator
from tenants.models import Tenant, TenantStatus
import logging

logger = logging.getLogger(__name__)


class TenantService:
    """
    Pure Django service for tenant operations
    No external dependencies - uses Django ORM directly
    """

    @staticmethod
    def get_tenants(filters: Optional[Dict[str, Any]] = None, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """
        Get list of tenants with filtering and pagination
        """
        try:
            queryset = Tenant.objects.select_related('current_location', 'user').all()

            # Apply filters
            if filters:
                search = filters.get('search')
                if search:
                    queryset = queryset.filter(
                        Q(name__icontains=search) |
                        Q(email__icontains=search) |
                        Q(phone__icontains=search) |
                        Q(id_number__icontains=search)
                    )

                status = filters.get('status')
                if status:
                    queryset = queryset.filter(tenant_status=status)

                tenant_type = filters.get('type')
                if tenant_type:
                    queryset = queryset.filter(tenant_type=tenant_type)

                compliance_status = filters.get('compliance_status')
                if compliance_status:
                    queryset = queryset.filter(compliance_status=compliance_status)

            # Paginate
            paginator = Paginator(queryset, page_size)
            page_obj = paginator.get_page(page)

            # Serialize data
            tenant_data = [
                {
                    'id': str(tenant.id),
                    'name': tenant.name,
                    'email': tenant.email,
                    'phone': tenant.phone,
                    'id_number': tenant.id_number,
                    'tenant_type': tenant.tenant_type,
                    'tenant_status': tenant.tenant_status,
                    'compliance_status': tenant.compliance_status,
                    'account_balance': float(tenant.account_balance),
                    'current_location': {
                        'id': str(tenant.current_location.id),
                        'name': tenant.current_location.name
                    } if tenant.current_location else None,
                    'created_at': tenant.created_at.isoformat(),
                }
                for tenant in page_obj
            ]

            return {
                'success': True,
                'data': tenant_data,
                'total': paginator.count,
                'page': page,
                'pages': paginator.num_pages,
            }

        except Exception as e:
            logger.error(f"Error getting tenants: {e}")
            return {
                'success': False,
                'error': str(e),
                'data': []
            }

    @staticmethod
    def get_tenant(tenant_id: str) -> Dict[str, Any]:
        """
        Get single tenant by ID with enriched data
        """
        try:
            tenant = Tenant.objects.select_related('current_location', 'user').get(id=tenant_id)

            # Get financial summary
            financial = tenant.financial_summary

            # Get rental agreement info
            from rentals.models import RentalAgreement
            active_agreement = RentalAgreement.objects.filter(
                tenant=tenant,
                status='active'
            ).select_related('room', 'room__location').first()

            # Get payment history count
            payment_count = tenant.payments.filter(status='completed').count()

            # Get maintenance request count
            maintenance_count = tenant.maintenance_requests.count()

            tenant_data = {
                'id': str(tenant.id),
                'name': tenant.name,
                'email': tenant.email,
                'phone': tenant.phone,
                'id_number': tenant.id_number,
                'tenant_type': tenant.tenant_type,
                'tenant_status': tenant.tenant_status,
                'compliance_status': tenant.compliance_status,
                'compliance_notes': tenant.compliance_notes,
                'account_balance': float(tenant.account_balance),
                'emergency_contact_name': tenant.emergency_contact_name,
                'emergency_contact_phone': tenant.emergency_contact_phone,
                'institution_employer': tenant.institution_employer,
                'current_location': {
                    'id': str(tenant.current_location.id),
                    'name': tenant.current_location.name,
                    'code': tenant.current_location.code
                } if tenant.current_location else None,
                'active_agreement': {
                    'id': str(active_agreement.id),
                    'room_number': active_agreement.room.room_number,
                    'location': active_agreement.room.location.name,
                    'rent_amount': float(active_agreement.rent_amount),
                    'start_date': active_agreement.start_date.isoformat(),
                    'end_date': active_agreement.end_date.isoformat(),
                } if active_agreement else None,
                'financial_summary': financial,
                'payment_count': payment_count,
                'maintenance_count': maintenance_count,
                'created_at': tenant.created_at.isoformat(),
                'updated_at': tenant.updated_at.isoformat(),
            }

            return {
                'success': True,
                'data': tenant_data
            }

        except Tenant.DoesNotExist:
            return {
                'success': False,
                'error': 'Tenant not found'
            }
        except Exception as e:
            logger.error(f"Error getting tenant {tenant_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def create_tenant(tenant_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create new tenant
        """
        try:
            tenant = Tenant.objects.create(
                name=tenant_data['name'],
                email=tenant_data.get('email'),
                phone=tenant_data.get('phone'),
                id_number=tenant_data.get('id_number'),
                tenant_type=tenant_data.get('tenant_type', 'other'),
                tenant_status=tenant_data.get('tenant_status', 'prospective'),
                emergency_contact_name=tenant_data.get('emergency_contact_name'),
                emergency_contact_phone=tenant_data.get('emergency_contact_phone'),
                institution_employer=tenant_data.get('institution_employer'),
            )

            return {
                'success': True,
                'data': {
                    'id': str(tenant.id),
                    'name': tenant.name,
                    'email': tenant.email,
                    'phone': tenant.phone,
                    'tenant_status': tenant.tenant_status,
                    'created_at': tenant.created_at.isoformat(),
                },
                'message': 'Tenant created successfully'
            }

        except Exception as e:
            logger.error(f"Error creating tenant: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def update_tenant(tenant_id: str, tenant_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update existing tenant
        """
        try:
            tenant = Tenant.objects.get(id=tenant_id)

            # Update fields
            for field, value in tenant_data.items():
                if hasattr(tenant, field) and value is not None:
                    setattr(tenant, field, value)

            tenant.save()

            return {
                'success': True,
                'data': {
                    'id': str(tenant.id),
                    'name': tenant.name,
                    'updated_at': tenant.updated_at.isoformat(),
                },
                'message': 'Tenant updated successfully'
            }

        except Tenant.DoesNotExist:
            return {
                'success': False,
                'error': 'Tenant not found'
            }
        except Exception as e:
            logger.error(f"Error updating tenant {tenant_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def delete_tenant(tenant_id: str) -> Dict[str, Any]:
        """
        Delete tenant (with validation)
        """
        try:
            tenant = Tenant.objects.get(id=tenant_id)

            # Validate deletion
            from rentals.models import RentalAgreement
            active_agreements = RentalAgreement.objects.filter(
                tenant=tenant,
                status='active'
            ).count()

            if active_agreements > 0:
                return {
                    'success': False,
                    'error': f'Cannot delete tenant with {active_agreements} active rental agreement(s)'
                }

            tenant_name = tenant.name
            tenant.delete()

            return {
                'success': True,
                'tenant_name': tenant_name,
                'message': f'Tenant "{tenant_name}" deleted successfully'
            }

        except Tenant.DoesNotExist:
            return {
                'success': False,
                'error': 'Tenant not found'
            }
        except Exception as e:
            logger.error(f"Error deleting tenant {tenant_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def validate_tenant_deletion(tenant_id: str) -> Dict[str, Any]:
        """
        Validate if tenant can be deleted
        """
        try:
            tenant = Tenant.objects.get(id=tenant_id)

            from rentals.models import RentalAgreement
            from payments.models import Payment

            # Check active agreements
            active_agreements = list(
                RentalAgreement.objects.filter(
                    tenant=tenant,
                    status='active'
                ).select_related('room', 'room__location').values(
                    'id', 'agreement_number', 'room__room_number', 'room__location__name'
                )
            )

            # Check outstanding payments
            outstanding_payments = list(
                Payment.objects.filter(
                    tenant=tenant,
                    status='pending'
                ).values('id', 'payment_number', 'amount', 'payment_date')
            )

            can_delete = len(active_agreements) == 0 and len(outstanding_payments) == 0

            warnings = []
            if active_agreements:
                warnings.append(f'{len(active_agreements)} active rental agreement(s) found')
            if outstanding_payments:
                warnings.append(f'{len(outstanding_payments)} outstanding payment(s) found')

            return {
                'success': True,
                'data': {
                    'can_delete': can_delete,
                    'active_agreements': active_agreements,
                    'outstanding_payments': outstanding_payments,
                    'warnings': warnings
                }
            }

        except Tenant.DoesNotExist:
            return {
                'success': False,
                'error': 'Tenant not found'
            }
        except Exception as e:
            logger.error(f"Error validating tenant deletion {tenant_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def get_workflow_status(tenant_id: str, user) -> Dict[str, Any]:
        """
        Get workflow status for tenant compliance management
        """
        try:
            tenant = Tenant.objects.get(id=tenant_id)

            # Use the tenant compliance workflow engine
            from workflows.tenant import TenantComplianceWorkflowEngine
            workflow = TenantComplianceWorkflowEngine(tenant)

            # Get current state and available events
            current_state = workflow.get_current_state()
            available_events = workflow._get_available_events(user)

            # Get workflow history
            from workflows.services import AuditLogService
            workflow_history = AuditLogService.get_workflow_history('Tenant', tenant_id)

            # Get compliance metrics
            compliance_metrics = workflow.get_violation_metrics()

            return {
                'success': True,
                'data': {
                    'current_state': current_state,
                    'available_events': available_events,
                    'workflow_history': workflow_history,
                    'compliance_status': tenant.compliance_status,
                    'violation_count': getattr(tenant, 'violation_count', 0),
                    'days_in_current_status': compliance_metrics.get('days_in_current_status', 0),
                    'compliance_history': compliance_metrics.get('compliance_history', []),
                }
            }

        except Tenant.DoesNotExist:
            return {
                'success': False,
                'error': 'Tenant not found'
            }
        except Exception as e:
            logger.error(f"Error getting tenant workflow status {tenant_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

