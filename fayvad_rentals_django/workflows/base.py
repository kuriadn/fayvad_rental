"""
Base Workflow Engine
Provides state machine functionality and common workflow operations
"""

from typing import Dict, List, Optional, Any, Callable, Tuple
from abc import ABC, abstractmethod
from enum import Enum
from django.db import models, transaction
from django.utils import timezone
from django.core.exceptions import ValidationError, PermissionDenied
import logging
logger = logging.getLogger(__name__)


class WorkflowTransitionError(Exception):
    """Exception raised when workflow transition fails"""
    pass


class WorkflowPermissionError(PermissionDenied):
    """Exception raised when user lacks workflow permissions"""
    pass


class WorkflowState(Enum):
    """Base workflow state enumeration"""
    pass


class WorkflowEvent(Enum):
    """Base workflow event enumeration"""
    pass


class WorkflowTransition:
    """Represents a workflow state transition"""

    def __init__(self,
                 from_states: List[str],
                 to_state: str,
                 event: str,
                 required_permissions: Optional[List[str]] = None,
                 validators: Optional[List[Callable]] = None,
                 side_effects: Optional[List[Callable]] = None,
                 description: str = ""):
        self.from_states = from_states
        self.to_state = to_state
        self.event = event
        self.required_permissions = required_permissions or []
        self.validators = validators or []
        self.side_effects = side_effects or []
        self.description = description


class WorkflowEngine(ABC):
    """
    Base workflow engine providing state machine functionality
    """

    def __init__(self, instance: models.Model):
        from django.contrib.auth import get_user_model
        self.User = get_user_model()
        self.instance = instance
        self.transitions = self._define_transitions()
        self.audit_log = []

    @abstractmethod
    def _define_transitions(self) -> Dict[str, WorkflowTransition]:
        """Define all possible transitions for this workflow"""
        pass

    @abstractmethod
    def _get_status_field(self) -> str:
        """Return the field name that stores the current status"""
        pass

    @abstractmethod
    def _get_available_events(self, user) -> List[str]:
        """Get events available to the current user"""
        pass

    def get_current_state(self) -> str:
        """Get current workflow state"""
        return getattr(self.instance, self._get_status_field())

    def can_transition(self, event: str, user, **kwargs) -> Tuple[bool, str]:
        """
        Check if transition is allowed
        Returns (allowed, reason)
        """
        if event not in self.transitions:
            return False, f"Unknown event: {event}"

        transition = self.transitions[event]
        current_state = self.get_current_state()

        # Check if current state allows this transition
        if current_state not in transition.from_states:
            return False, f"Cannot {event} from {current_state} state"

        # Check permissions
        if not self._check_permissions(user, transition.required_permissions):
            return False, "Insufficient permissions"

        # Run validators
        for validator in transition.validators:
            try:
                result = validator(self.instance, user, **kwargs)
                if not result[0]:
                    return False, result[1]
            except Exception as e:
                logger.error(f"Validator error for {event} on {validator.__name__}: {e}")
                return False, f"Validation error: {str(e)}"

        return True, "OK"

    def transition(self, event: str, user, **kwargs) -> Dict[str, Any]:
        """
        Execute workflow transition
        """
        try:
            # Check if transition is allowed (outside transaction)
            allowed, reason = self.can_transition(event, user, **kwargs)
            if not allowed:
                raise WorkflowTransitionError(reason)

            transition = self.transitions[event]
            old_state = self.get_current_state()

            with transaction.atomic():
                # Execute side effects before transition
                for side_effect in transition.side_effects:
                    try:
                        side_effect(self.instance, user, **kwargs)
                    except Exception as e:
                        logger.error(f"Side effect error for {event}: {e}")
                        raise WorkflowTransitionError(f"Side effect failed: {str(e)}")

                # Update state
                setattr(self.instance, self._get_status_field(), transition.to_state)
                self.instance.save()

            # Log the transition and execute post-transition actions (outside transaction)
            # These should not fail the main state transition
            try:
                self._log_transition(event, old_state, transition.to_state, user, **kwargs)
            except Exception as e:
                logger.warning(f"Failed to log transition: {e}")

            try:
                self._execute_post_transition_actions(event, user, **kwargs)
            except Exception as e:
                logger.warning(f"Failed to execute post-transition actions: {e}")

            return {
                'success': True,
                'old_state': old_state,
                'new_state': transition.to_state,
                'event': event,
                'message': f"Successfully transitioned to {transition.to_state}"
            }

        except WorkflowTransitionError:
            raise
        except Exception as e:
            logger.error(f"Workflow transition error for {event}: {e}")
            raise WorkflowTransitionError(f"Transition failed: {str(e)}")

    def _check_permissions(self, user, required_permissions: List[str]) -> bool:
        """Check if user has required permissions"""
        if not required_permissions:
            return True

        # Superusers can perform any action
        if user.is_superuser:
            return True

        for permission in required_permissions:
            if permission == 'staff' and not user.is_staff:
                return False
            elif permission == 'superuser' and not user.is_superuser:
                return False
            elif permission.startswith('group:'):
                group_name = permission.split(':', 1)[1]
                if not user.groups.filter(name=group_name).exists():
                    return False
            elif permission.startswith('role:'):
                role_name = permission.split(':', 1)[1]
                if not self._check_staff_role(user, role_name):
                    return False

        return True

    def _check_staff_role(self, user, required_role: str) -> bool:
        """Check if user has specific staff role"""
        try:
            staff_profile = user.staff_profile
            if not staff_profile or not staff_profile.is_active_staff:
                return False

            # Check exact role match
            if staff_profile.role == required_role:
                return True

            # Check role hierarchies/permissions
            if required_role == 'manager':
                # Only managers have manager permissions
                return staff_profile.role == 'manager'
            elif required_role == 'caretaker':
                # Managers and caretakers have caretaker permissions
                return staff_profile.role in ['manager', 'caretaker']
            elif required_role == 'cleaner':
                # Managers, caretakers, and cleaners have cleaner permissions
                return staff_profile.role in ['manager', 'caretaker', 'cleaner']
            elif required_role == 'maintenance_tech':
                # Anyone can be a maintenance technician if assigned
                return staff_profile.role in ['manager', 'caretaker', 'maintenance']

        except AttributeError:
            # User has no staff profile
            return False

        return False

    def _log_transition(self, event: str, old_state: str, new_state: str,
                       user, **kwargs):
        """Log workflow transition"""
        from .services import AuditLogService

        log_entry = {
            'instance_type': self.instance.__class__.__name__,
            'instance_id': str(self.instance.id),
            'event': event,
            'old_state': old_state,
            'new_state': new_state,
            'user': user,
            'metadata': kwargs
        }

        self.audit_log.append(log_entry)

        # Log to audit service if available
        try:
            AuditLogService.log_workflow_transition(**log_entry)
        except Exception as e:
            logger.warning(f"Failed to log to audit service: {e}")

    def _execute_post_transition_actions(self, event: str, user, **kwargs):
        """Execute actions after successful transition"""
        from .services import NotificationService

        try:
            NotificationService.notify_workflow_transition(
                self.instance, event, user, **kwargs
            )
        except Exception as e:
            logger.warning(f"Failed to send notifications: {e}")

    def get_workflow_history(self) -> List[Dict[str, Any]]:
        """Get workflow history for this instance"""
        from .services import AuditLogService

        try:
            return AuditLogService.get_workflow_history(
                self.instance.__class__.__name__,
                str(self.instance.id)
            )
        except Exception as e:
            logger.warning(f"Failed to get workflow history: {e}")
            return self.audit_log

    def get_available_transitions(self, user) -> List[Dict[str, Any]]:
        """Get all available transitions for current user"""
        available = []
        for event, transition in self.transitions.items():
            allowed, reason = self.can_transition(event, user)
            if allowed:
                available.append({
                    'event': event,
                    'to_state': transition.to_state,
                    'description': transition.description,
                })

        return available

    def get_available_events(self, user) -> List[str]:
        """Get list of available event names for the current user"""
        available = []
        for event, transition in self.transitions.items():
            # Check if user has permission for this transition (ignore parameter validation for UI)
            current_state = self.get_current_state()
            if current_state not in transition.from_states:
                continue

            if not self._check_permissions(user, transition.required_permissions):
                continue

            # For UI purposes, include events that user has permission for
            # Parameter validation happens when the action is actually performed
            available.append(event)
        return available

    @classmethod
    def get_workflow_for_instance(cls, instance: models.Model) -> 'WorkflowEngine':
        """Factory method to get appropriate workflow for instance"""
        from .maintenance import MaintenanceWorkflowEngine
        from .payment import PaymentWorkflowEngine

        if hasattr(instance, 'priority'):  # MaintenanceRequest
            return MaintenanceWorkflowEngine(instance)
        elif hasattr(instance, 'payment_method'):  # Payment
            return PaymentWorkflowEngine(instance)
        else:
            raise ValueError(f"No workflow available for {type(instance)}")
