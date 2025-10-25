"""
Complaint Service - Handles complaint management operations
"""

from typing import Dict, List, Optional, Any
from django.db.models import Q, Count
from django.core.paginator import Paginator
from tenants.models import Complaint, ComplaintStatus, ComplaintPriority, ComplaintCategory
import logging

logger = logging.getLogger(__name__)


class ComplaintService:
    """
    Service for complaint management operations
    """

    @staticmethod
    def get_complaints(filters: Optional[Dict[str, Any]] = None, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """
        Get list of complaints with filtering and pagination
        """
        try:
            queryset = Complaint.objects.select_related(
                'tenant', 'room__location', 'assigned_to__user'
            ).all()

            # Apply filters
            if filters:
                search = filters.get('search')
                if search:
                    queryset = queryset.filter(
                        Q(complaint_number__icontains=search) |
                        Q(subject__icontains=search) |
                        Q(description__icontains=search) |
                        Q(tenant__name__icontains=search)
                    )

                status = filters.get('status')
                if status:
                    queryset = queryset.filter(status=status)

                priority = filters.get('priority')
                if priority:
                    queryset = queryset.filter(priority=priority)

                category = filters.get('category')
                if category:
                    queryset = queryset.filter(category=category)

                assigned_to = filters.get('assigned_to')
                if assigned_to:
                    queryset = queryset.filter(assigned_to=assigned_to)

                tenant_id = filters.get('tenant_id')
                if tenant_id:
                    queryset = queryset.filter(tenant_id=tenant_id)

                date_from = filters.get('date_from')
                if date_from:
                    queryset = queryset.filter(created_at__date__gte=date_from)

                date_to = filters.get('date_to')
                if date_to:
                    queryset = queryset.filter(created_at__date__lte=date_to)

            # Pagination
            paginator = Paginator(queryset, page_size)
            page_obj = paginator.get_page(page)

            return {
                'success': True,
                'data': {
                    'complaints': list(page_obj.object_list.values(
                        'id', 'complaint_number', 'subject', 'category', 'priority',
                        'status', 'created_at', 'is_overdue',
                        'tenant__name', 'tenant__id',
                        'room__room_number', 'room__location__name',
                        'assigned_to__user__first_name', 'assigned_to__user__last_name'
                    )),
                    'pagination': {
                        'page': page,
                        'total_pages': paginator.num_pages,
                        'total_items': paginator.count,
                        'has_next': page_obj.has_next(),
                        'has_previous': page_obj.has_previous(),
                    }
                }
            }

        except Exception as e:
            logger.error(f"Error getting complaints: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def get_complaint(complaint_id: str) -> Dict[str, Any]:
        """
        Get single complaint details
        """
        try:
            complaint = Complaint.objects.select_related(
                'tenant', 'room__location', 'assigned_to__user'
            ).get(id=complaint_id)

            return {
                'success': True,
                'data': {
                    'id': str(complaint.id),
                    'complaint_number': complaint.complaint_number,
                    'subject': complaint.subject,
                    'description': complaint.description,
                    'category': complaint.category,
                    'priority': complaint.priority,
                    'status': complaint.status,
                    'resolution': complaint.resolution,
                    'resolution_date': complaint.resolution_date.isoformat() if complaint.resolution_date else None,
                    'is_overdue': complaint.is_overdue,
                    'days_open': complaint.days_open,
                    'is_anonymous': complaint.is_anonymous,
                    'contact_preference': complaint.contact_preference,
                    'created_at': complaint.created_at.isoformat(),
                    'updated_at': complaint.updated_at.isoformat(),
                    'tenant': {
                        'id': str(complaint.tenant.id),
                        'name': complaint.tenant.name,
                        'email': complaint.tenant.email,
                        'phone': complaint.tenant.phone,
                    } if complaint.tenant else None,
                    'room': {
                        'id': str(complaint.room.id),
                        'room_number': complaint.room.room_number,
                        'location_name': complaint.room.location.name if complaint.room.location else None,
                    } if complaint.room else None,
                    'assigned_to': {
                        'id': str(complaint.assigned_to.id),
                        'name': complaint.assigned_to.user.get_full_name(),
                        'email': complaint.assigned_to.email,
                    } if complaint.assigned_to else None,
                }
            }

        except Complaint.DoesNotExist:
            return {
                'success': False,
                'error': 'Complaint not found'
            }
        except Exception as e:
            logger.error(f"Error getting complaint {complaint_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def create_complaint(complaint_data: Dict[str, Any], user) -> Dict[str, Any]:
        """
        Create a new complaint
        """
        try:
            # Validate required fields
            required_fields = ['subject', 'description', 'category', 'tenant']
            for field in required_fields:
                if field not in complaint_data or not complaint_data[field]:
                    return {
                        'success': False,
                        'error': f'{field} is required'
                    }

            complaint = Complaint.objects.create(**complaint_data)

            # Trigger workflow
            from workflows.complaint import ComplaintWorkflowEngine
            workflow = ComplaintWorkflowEngine(complaint)
            workflow.transition('submit_complaint', user)

            return {
                'success': True,
                'data': {
                    'id': str(complaint.id),
                    'complaint_number': complaint.complaint_number,
                    'status': complaint.status,
                },
                'message': 'Complaint created successfully'
            }

        except Exception as e:
            logger.error(f"Error creating complaint: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def update_complaint(complaint_id: str, update_data: Dict[str, Any], user) -> Dict[str, Any]:
        """
        Update complaint details
        """
        try:
            complaint = Complaint.objects.get(id=complaint_id)

            # Update fields
            for field, value in update_data.items():
                if hasattr(complaint, field):
                    setattr(complaint, field, value)

            complaint.save()

            return {
                'success': True,
                'data': {
                    'id': str(complaint.id),
                    'complaint_number': complaint.complaint_number,
                    'status': complaint.status,
                },
                'message': 'Complaint updated successfully'
            }

        except Complaint.DoesNotExist:
            return {
                'success': False,
                'error': 'Complaint not found'
            }
        except Exception as e:
            logger.error(f"Error updating complaint {complaint_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def get_workflow_status(complaint_id: str, user) -> Dict[str, Any]:
        """
        Get workflow status for complaint
        """
        try:
            complaint = Complaint.objects.get(id=complaint_id)

            # Use the complaint workflow engine
            from workflows.complaint import ComplaintWorkflowEngine
            workflow = ComplaintWorkflowEngine(complaint)

            # Get current state and available events
            current_state = workflow.get_current_state()
            available_events = workflow._get_available_events(user)

            # Get workflow history
            workflow_history = workflow.get_complaint_history()

            # Get complaint metrics
            metrics = workflow.get_complaint_metrics()

            return {
                'success': True,
                'data': {
                    'current_state': current_state,
                    'available_events': available_events,
                    'workflow_history': workflow_history,
                    'status': complaint.status,
                    'complaint_number': complaint.complaint_number,
                    'priority': complaint.priority,
                    'days_open': complaint.days_open,
                    'is_overdue': complaint.is_overdue,
                    'assigned_staff': metrics.get('assigned_staff'),
                    'escalation_deadline': metrics.get('escalation_deadline'),
                }
            }

        except Complaint.DoesNotExist:
            return {
                'success': False,
                'error': 'Complaint not found'
            }
        except Exception as e:
            logger.error(f"Error getting complaint workflow status {complaint_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def get_complaint_statistics() -> Dict[str, Any]:
        """
        Get complaint statistics for dashboard
        """
        try:
            total_complaints = Complaint.objects.count()
            open_complaints = Complaint.objects.filter(status='open').count()
            investigating_complaints = Complaint.objects.filter(status='investigating').count()
            resolved_complaints = Complaint.objects.filter(status='resolved').count()
            closed_complaints = Complaint.objects.filter(status='closed').count()

            # Priority breakdown
            priority_stats = Complaint.objects.values('priority').annotate(
                count=Count('priority')
            ).order_by('priority')

            # Category breakdown
            category_stats = Complaint.objects.values('category').annotate(
                count=Count('category')
            ).order_by('category')

            # Overdue complaints
            overdue_count = sum(1 for c in Complaint.objects.filter(
                status__in=['open', 'investigating']
            ) if c.is_overdue)

            # Average resolution time (for resolved complaints)
            resolved_qs = Complaint.objects.filter(status__in=['resolved', 'closed'])
            avg_resolution_days = 0
            if resolved_qs.exists():
                total_days = sum(c.days_open for c in resolved_qs)
                avg_resolution_days = total_days / resolved_qs.count()

            return {
                'success': True,
                'data': {
                    'total_complaints': total_complaints,
                    'open_complaints': open_complaints,
                    'investigating_complaints': investigating_complaints,
                    'resolved_complaints': resolved_complaints,
                    'closed_complaints': closed_complaints,
                    'overdue_complaints': overdue_count,
                    'avg_resolution_days': round(avg_resolution_days, 1),
                    'priority_breakdown': list(priority_stats),
                    'category_breakdown': list(category_stats),
                }
            }

        except Exception as e:
            logger.error(f"Error getting complaint statistics: {e}")
            return {
                'success': False,
                'error': str(e)
            }
