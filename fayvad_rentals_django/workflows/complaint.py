"""
Simple Complaint Workflow Engine
Provides basic workflow functionality for complaint management
"""

from typing import List, Dict, Any
from django.contrib.auth import get_user_model
from tenants.models import Complaint, ComplaintStatus
from core_services.workflow_service import SimpleWorkflowService

User = get_user_model()


class ComplaintWorkflowEngine:
    """
    Simple workflow engine for complaint state management
    Uses the SimpleWorkflowService for state transitions
    """

    def __init__(self, complaint: Complaint):
        self.complaint = complaint
        self.workflow_service = SimpleWorkflowService()

    def get_current_state(self) -> str:
        """Get the current state of the complaint"""
        return self.complaint.status

    def _get_available_events(self, user: User) -> List[str]:
        """
        Get available state transition events for the current user
        Based on user permissions and current complaint state
        """
        current_state = self.get_current_state()
        available_transitions = self.workflow_service.get_valid_transitions('Complaint', current_state)

        # Filter based on user permissions
        if not user.is_staff and not user.groups.filter(name__in=['Manager', 'Admin']).exists():
            # Non-staff users can only view, not change status
            return []

        # Return available transitions as "events"
        return available_transitions

    def get_complaint_metrics(self) -> Dict[str, Any]:
        """Get basic metrics about the complaint"""
        from django.utils import timezone

        metrics = {
            'days_open': None,
            'is_overdue': False,
            'priority_level': self.complaint.priority,
            'category': self.complaint.category,
            'has_assignment': self.complaint.assigned_to is not None,
        }

        if self.complaint.created_at:
            days_open = (timezone.now() - self.complaint.created_at).days
            metrics['days_open'] = days_open

            # Check if overdue based on priority and SLA
            if self.complaint.escalation_deadline:
                metrics['is_overdue'] = timezone.now() > self.complaint.escalation_deadline

        return metrics

    def get_complaint_history(self) -> List[Dict[str, Any]]:
        """
        Get complaint status change history
        Note: This is a simplified version. In a full implementation,
        you'd want to track status changes in a separate audit table.
        """
        # For now, return basic info about the complaint
        # In a real implementation, you'd query an audit log
        history = [{
            'timestamp': self.complaint.created_at,
            'from_status': None,
            'to_status': self.complaint.status,
            'user': None,  # Would be the user who created it
            'notes': 'Complaint created'
        }]

        if self.complaint.resolution_date:
            history.append({
                'timestamp': self.complaint.resolution_date,
                'from_status': self.complaint.status,
                'to_status': ComplaintStatus.RESOLVED,
                'user': None,  # Would be the user who resolved it
                'notes': self.complaint.resolution or 'Complaint resolved'
            })

        return history
