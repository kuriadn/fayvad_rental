"""
Dashboard URLs
"""

from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Dashboard views
    path('', views.dashboard_overview, name='dashboard_overview'),
    path('overview/', views.dashboard_overview, name='dashboard_overview_alt'),
    path('financial/', views.dashboard_financial, name='dashboard_financial'),
    path('occupancy/', views.dashboard_occupancy, name='dashboard_occupancy'),
    path('maintenance/', views.dashboard_maintenance, name='dashboard_maintenance'),
    path('tenant/', views.dashboard_tenant, name='dashboard_tenant'),
    path('property/', views.dashboard_property, name='dashboard_property'),
    path('audit-log/', views.audit_log_view, name='audit_log'),

    # API endpoints for real-time updates
    path('api/metrics/', views.dashboard_metrics_api, name='dashboard_metrics_api'),
]
