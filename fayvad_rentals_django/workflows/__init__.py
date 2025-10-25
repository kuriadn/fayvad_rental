"""
Workflow Engine for Fayvad Rentals
Provides state machine functionality for business processes
"""

# Lazy imports to avoid circular dependencies during Django app loading
def __getattr__(name):
    if name == 'WorkflowEngine':
        from .base import WorkflowEngine
        return WorkflowEngine
    elif name == 'MaintenanceWorkflowEngine':
        from .maintenance import MaintenanceWorkflowEngine
        return MaintenanceWorkflowEngine
    elif name == 'PaymentWorkflowEngine':
        from .payment import PaymentWorkflowEngine
        return PaymentWorkflowEngine
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = [
    'WorkflowEngine',
    'MaintenanceWorkflowEngine',
    'PaymentWorkflowEngine',
]
