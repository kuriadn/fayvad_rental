"""
Workflow API URLs
"""

from django.urls import path
from . import views

app_name = 'workflow_api'

urlpatterns = [
    # Simple workflow transitions
    path('transition/<str:model_type>/<int:instance_id>/', views.workflow_transition, name='workflow_transition'),


    # Removed complex workflow endpoints - replaced with simple state management
]
