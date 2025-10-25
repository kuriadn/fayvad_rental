"""
Workflow API URLs
"""

from django.urls import path
from . import views

app_name = 'workflow_api'

urlpatterns = [
    # Workflow status and actions
    path('<str:instance_type>/<str:instance_id>/status/', views.get_workflow_status, name='workflow_status'),
    path('<str:instance_type>/<str:instance_id>/action/', views.perform_workflow_action, name='workflow_action'),
    path('<str:instance_type>/<str:instance_id>/history/', views.get_workflow_history, name='workflow_history'),

    # Notifications
    path('notifications/', views.get_user_notifications, name='user_notifications'),
    path('notifications/mark-read/', views.mark_notifications_read, name='mark_notifications_read'),

    # Audit and reporting
    path('audit/summary/', views.get_workflow_audit_summary, name='audit_summary'),
]
