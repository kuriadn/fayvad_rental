"""
Maintenance Service - Pure Django Implementation
Manages maintenance requests with direct Django ORM
"""

from typing import Dict, List, Optional, Any
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from django.utils import timezone
from maintenance.models import MaintenanceRequest, Priority
import logging

User = get_user_model()

logger = logging.getLogger(__name__)


class MaintenanceService:
    """
    Pure Django service for maintenance request operations
    """

    @staticmethod
    def get_maintenance_requests(filters: Optional[Dict[str, Any]] = None, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """
        Get list of maintenance requests with filtering
        """
        try:
            queryset = MaintenanceRequest.objects.select_related(
                'tenant', 'room', 'room__location', 'created_by'
            ).all()

            # Apply filters
            if filters:
                search = filters.get('search')
                if search:
                    queryset = queryset.filter(
                        Q(request_number__icontains=search) |
                        Q(title__icontains=search) |
                        Q(tenant__name__icontains=search)
                    )

                status = filters.get('status')
                if status:
                    queryset = queryset.filter(status=status)

                priority = filters.get('priority')
                if priority:
                    queryset = queryset.filter(priority=priority)

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
            request_data = [
                {
                    'id': str(request.id),
                    'request_number': request.request_number,
                    'title': request.title,
                    'description': request.description,
                    'priority': request.priority,
                    'status': request.status,
                    'requested_date': request.requested_date.isoformat(),
                    'scheduled_date': request.scheduled_date.isoformat() if request.scheduled_date else None,
                    'tenant': {
                        'id': str(request.tenant.id),
                        'name': request.tenant.name
                    },
                    'room': {
                        'id': str(request.room.id),
                        'room_number': request.room.room_number,
                        'location': request.room.location.name
                    },
                    'assigned_to': request.assigned_to,
                    'is_pending': request.is_pending,
                    'is_overdue': request.is_overdue,
                    'days_pending': request.days_pending,
                }
                for request in page_obj
            ]

            return {
                'success': True,
                'data': request_data,
                'total': paginator.count,
                'page': page,
                'pages': paginator.num_pages,
            }

        except Exception as e:
            logger.error(f"Error getting maintenance requests: {e}")
            return {
                'success': False,
                'error': str(e),
                'data': []
            }

    @staticmethod
    def get_maintenance_request(request_id: str) -> Dict[str, Any]:
        """
        Get single maintenance request by ID
        """
        try:
            request = MaintenanceRequest.objects.select_related(
                'tenant', 'room', 'room__location', 'created_by'
            ).get(id=request_id)

            request_data = {
                'id': str(request.id),
                'request_number': request.request_number,
                'title': request.title,
                'description': request.description,
                'priority': request.priority,
                'status': request.status,
                'requested_date': request.requested_date.isoformat(),
                'scheduled_date': request.scheduled_date.isoformat() if request.scheduled_date else None,
                'completed_date': request.completed_date.isoformat() if request.completed_date else None,
                'tenant': {
                    'id': str(request.tenant.id),
                    'name': request.tenant.name,
                    'email': request.tenant.email,
                    'phone': request.tenant.phone
                },
                'room': {
                    'id': str(request.room.id),
                    'room_number': request.room.room_number,
                    'location': {
                        'id': str(request.room.location.id),
                        'name': request.room.location.name
                    }
                },
                'created_by': {
                    'id': request.created_by.id,
                    'name': f'{request.created_by.first_name} {request.created_by.last_name}'
                },
                'assigned_to': request.assigned_to,
                'assigned_date': request.assigned_date.isoformat() if request.assigned_date else None,
                'estimated_cost': float(request.estimated_cost) if request.estimated_cost else None,
                'actual_cost': float(request.actual_cost) if request.actual_cost else None,
                'cost_variance': request.cost_variance,
                'resolution_notes': request.resolution_notes,
                'resolution_photos': request.resolution_photos,
                'follow_up_required': request.follow_up_required,
                'follow_up_date': request.follow_up_date.isoformat() if request.follow_up_date else None,
                'follow_up_notes': request.follow_up_notes,
                'is_pending': request.is_pending,
                'is_in_progress': request.is_in_progress,
                'is_completed': request.is_completed,
                'is_overdue': request.is_overdue,
                'days_pending': request.days_pending,
                'days_to_completion': request.days_to_completion,
                'can_be_assigned': request.can_be_assigned,
                'can_be_completed': request.can_be_completed,
                'can_be_cancelled': request.can_be_cancelled,
                'created_at': request.created_at.isoformat(),
                'updated_at': request.updated_at.isoformat(),
            }

            return {
                'success': True,
                'data': request_data
            }

        except MaintenanceRequest.DoesNotExist:
            return {
                'success': False,
                'error': 'Maintenance request not found'
            }
        except Exception as e:
            logger.error(f"Error getting maintenance request {request_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def create_maintenance_request(request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create new maintenance request
        """
        try:
            from tenants.models import Tenant
            from properties.models import Room
            from accounts.models import User

            tenant = Tenant.objects.get(id=request_data['tenant_id'])
            room = Room.objects.get(id=request_data['room_id'])
            created_by = User.objects.get(id=request_data['created_by_id'])

            maintenance_request = MaintenanceRequest.objects.create(
                title=request_data['title'],
                description=request_data['description'],
                tenant=tenant,
                room=room,
                created_by=created_by,
                priority=request_data.get('priority', 'medium'),
                estimated_cost=request_data.get('estimated_cost'),
            )

            return {
                'success': True,
                'data': {
                    'id': str(maintenance_request.id),
                    'request_number': maintenance_request.request_number,
                    'title': maintenance_request.title,
                    'priority': maintenance_request.priority,
                    'status': maintenance_request.status,
                    'created_at': maintenance_request.created_at.isoformat(),
                },
                'message': 'Maintenance request created successfully'
            }

        except (Tenant.DoesNotExist, Room.DoesNotExist, User.DoesNotExist) as e:
            return {
                'success': False,
                'error': str(e)
            }
        except Exception as e:
            logger.error(f"Error creating maintenance request: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def assign_technician(request_id: str, technician_name: str, user: User) -> Dict[str, Any]:
        """
        Assign technician to maintenance request
        Requires: caretaker or manager role
        """
        try:
            maintenance_request = MaintenanceRequest.objects.get(id=request_id)

            # Update assignment fields directly
            maintenance_request.assigned_to = technician_name
            maintenance_request.assigned_date = timezone.now()

            # Change status to in_progress if currently pending
            from .workflow_service import SimpleWorkflowService
            if maintenance_request.status == 'pending':
                workflow_result = SimpleWorkflowService.transition_state(
                    maintenance_request, 'in_progress', user
                )
                if not workflow_result['success']:
                    return {
                        'success': False,
                        'error': workflow_result['error']
                    }

            maintenance_request.save()

            return {
                'success': True,
                'data': {
                    'id': str(maintenance_request.id),
                    'assigned_to': maintenance_request.assigned_to,
                    'assigned_date': maintenance_request.assigned_date.isoformat() if maintenance_request.assigned_date else None,
                    'status': maintenance_request.status,
                },
                'message': f'Maintenance request assigned to {technician_name}'
            }

        except MaintenanceRequest.DoesNotExist:
            return {
                'success': False,
                'error': 'Maintenance request not found'
            }
        except Exception as e:
            logger.error(f"Error assigning technician to request {request_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def complete_request(request_id: str, user: User, resolution_notes: Optional[str] = None, actual_cost: Optional[float] = None) -> Dict[str, Any]:
        """
        Complete maintenance request using workflow engine
        Requires: caretaker or manager role
        """
        try:
            maintenance_request = MaintenanceRequest.objects.get(id=request_id)

            # Update completion fields directly
            maintenance_request.completed_date = timezone.now()
            if resolution_notes:
                maintenance_request.resolution_notes = resolution_notes
            if actual_cost is not None:
                maintenance_request.actual_cost = actual_cost

            # Change status to completed
            from .workflow_service import SimpleWorkflowService
            workflow_result = SimpleWorkflowService.transition_state(
                maintenance_request, 'completed', user
            )
            if not workflow_result['success']:
                return {
                    'success': False,
                    'error': workflow_result['error']
                }

            maintenance_request.save()

            return {
                'success': True,
                'data': {
                    'id': str(maintenance_request.id),
                    'status': maintenance_request.status,
                    'completed_date': maintenance_request.completed_date.isoformat() if maintenance_request.completed_date else None,
                },
                'message': 'Maintenance request completed successfully'
            }

        except MaintenanceRequest.DoesNotExist:
            return {
                'success': False,
                'error': 'Maintenance request not found'
            }
        except Exception as e:
            logger.error(f"Error completing maintenance request {request_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def cancel_request(request_id: str, user: User, reason: Optional[str] = None) -> Dict[str, Any]:
        """
        Cancel maintenance request using workflow engine
        Requires: caretaker or manager role
        """
        try:
            maintenance_request = MaintenanceRequest.objects.get(id=request_id)

            # Change status to cancelled
            from .workflow_service import SimpleWorkflowService
            workflow_result = SimpleWorkflowService.transition_state(
                maintenance_request, 'cancelled', user
            )
            if not workflow_result['success']:
                return {
                    'success': False,
                    'error': workflow_result['error']
                }

            # Store cancellation reason in resolution_notes if provided
            if reason:
                maintenance_request.resolution_notes = f"Cancelled: {reason}"
                maintenance_request.save()

            return {
                'success': True,
                'data': {
                    'id': str(maintenance_request.id),
                    'status': maintenance_request.status,
                },
                'message': 'Maintenance request cancelled successfully'
            }

        except MaintenanceRequest.DoesNotExist:
            return {
                'success': False,
                'error': 'Maintenance request not found'
            }
        except Exception as e:
            logger.error(f"Error cancelling maintenance request {request_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def schedule_maintenance(request_id: str, user: User, scheduled_date) -> Dict[str, Any]:
        """
        Schedule maintenance request using workflow engine
        Requires: caretaker or manager role
        """
        try:
            maintenance_request = MaintenanceRequest.objects.get(id=request_id)

            # Update scheduled date directly
            maintenance_request.scheduled_date = scheduled_date
            maintenance_request.save()

            return {
                'success': True,
                'data': {
                    'id': str(maintenance_request.id),
                    'scheduled_date': maintenance_request.scheduled_date.isoformat() if maintenance_request.scheduled_date else None,
                    'status': maintenance_request.status,
                },
                'message': f'Maintenance scheduled for {scheduled_date}'
            }

        except MaintenanceRequest.DoesNotExist:
            return {
                'success': False,
                'error': 'Maintenance request not found'
            }
        except Exception as e:
            logger.error(f"Error scheduling maintenance request {request_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def start_work(request_id: str, user: User, work_notes: Optional[str] = None) -> Dict[str, Any]:
        """
        Start work on maintenance request using workflow engine
        Requires: staff role
        """
        try:
            maintenance_request = MaintenanceRequest.objects.get(id=request_id)

            # Change status to in_progress
            from .workflow_service import SimpleWorkflowService
            workflow_result = SimpleWorkflowService.transition_state(
                maintenance_request, 'in_progress', user
            )
            if not workflow_result['success']:
                return {
                    'success': False,
                    'error': workflow_result['error']
                }

            return {
                'success': True,
                'data': {
                    'id': str(maintenance_request.id),
                    'status': maintenance_request.status,
                },
                'message': 'Work started on maintenance request'
            }

        except MaintenanceRequest.DoesNotExist:
            return {
                'success': False,
                'error': 'Maintenance request not found'
            }
        except Exception as e:
            logger.error(f"Error starting work on maintenance request {request_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def escalate_priority(request_id: str, user: User, new_priority: Optional[str] = None) -> Dict[str, Any]:
        """
        Escalate maintenance request priority using workflow engine
        Requires: manager role
        """
        try:
            maintenance_request = MaintenanceRequest.objects.get(id=request_id)

            # Update priority directly
            if new_priority:
                maintenance_request.priority = new_priority
                maintenance_request.save()

            return {
                'success': True,
                'data': {
                    'id': str(maintenance_request.id),
                    'priority': maintenance_request.priority,
                    'status': maintenance_request.status,
                },
                'message': f'Priority escalated to {maintenance_request.get_priority_display()}'
            }

        except MaintenanceRequest.DoesNotExist:
            return {
                'success': False,
                'error': 'Maintenance request not found'
            }
        except Exception as e:
            logger.error(f"Error escalating maintenance request {request_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }


    @staticmethod
    def get_overdue_requests() -> Dict[str, Any]:
        """
        Get all overdue maintenance requests
        """
        try:
            requests = MaintenanceRequest.objects.filter(
                status__in=['pending', 'in_progress']
            ).select_related('tenant', 'room', 'room__location')

            overdue_requests = [
                {
                    'id': str(request.id),
                    'request_number': request.request_number,
                    'title': request.title,
                    'priority': request.priority,
                    'days_pending': request.days_pending,
                    'tenant': request.tenant.name,
                    'room': f'{request.room.location.code}-{request.room.room_number}',
                }
                for request in requests if request.is_overdue
            ]

            return {
                'success': True,
                'data': overdue_requests,
                'count': len(overdue_requests)
            }

        except Exception as e:
            logger.error(f"Error getting overdue requests: {e}")
            return {
                'success': False,
                'error': str(e)
            }

