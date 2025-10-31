"""
Simple Workflow Service for Rental Management
Replaces complex workflow engines with basic state management
"""

from django.db import models
from typing import Dict, List, Any, Optional
from django.contrib.auth import get_user_model

User = get_user_model()


class SimpleWorkflowService:
    """
    Simple state management for rental workflows
    No complex triggers or conditions - just basic state transitions
    """

    # Define valid state transitions for each model type
    STATE_TRANSITIONS = {
        'MaintenanceRequest': {
            'pending': ['in_progress', 'cancelled'],
            'in_progress': ['completed', 'cancelled'],
            'completed': [],  # Terminal state
            'cancelled': []   # Terminal state
        },
        'Payment': {
            'pending': ['completed', 'failed'],
            'completed': [],  # Terminal state
            'failed': ['pending']  # Can retry failed payments
        },
        'RentalAgreement': {
            'draft': ['active', 'cancelled'],
            'active': ['completed', 'terminated'],
            'completed': [],  # Terminal state
            'terminated': [],  # Terminal state
            'cancelled': []   # Terminal state
        },
        'Complaint': {
            'pending': ['in_progress', 'resolved'],
            'in_progress': ['resolved'],
            'resolved': []  # Terminal state
        }
    }

    @staticmethod
    def get_valid_transitions(model_type: str, current_state: str) -> List[str]:
        """
        Get valid state transitions for a model type and current state
        """
        return SimpleWorkflowService.STATE_TRANSITIONS.get(model_type, {}).get(current_state, [])

    @staticmethod
    def can_transition(model_type: str, current_state: str, new_state: str) -> bool:
        """
        Check if a state transition is valid
        """
        valid_transitions = SimpleWorkflowService.get_valid_transitions(model_type, current_state)
        return new_state in valid_transitions

    @staticmethod
    def transition_state(instance: models.Model, new_state: str, user: User = None, notes: str = "") -> Dict[str, Any]:
        """
        Perform a state transition on a model instance
        """
        model_type = instance.__class__.__name__
        current_state = getattr(instance, 'status', None)

        if not current_state:
            return {
                'success': False,
                'error': f'Model {model_type} does not have a status field'
            }

        if not SimpleWorkflowService.can_transition(model_type, current_state, new_state):
            return {
                'success': False,
                'error': f'Invalid transition from {current_state} to {new_state} for {model_type}'
            }

        # Update the state
        instance.status = new_state
        instance.save()

        # Simple logging - removed complex audit service
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Workflow transition: {model_type} {instance.id} from '{current_state}' to '{new_state}' by user {user}")

        return {
            'success': True,
            'old_status': current_state,
            'new_status': new_state
        }

    @staticmethod
    def get_status_summary(model_class: models.Model) -> Dict[str, int]:
        """
        Get status summary counts for a model
        """
        return dict(
            model_class.objects.values('status')
            .annotate(count=models.Count('status'))
            .values_list('status', 'count')
        )
