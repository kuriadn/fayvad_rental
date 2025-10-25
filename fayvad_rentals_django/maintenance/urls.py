"""
Maintenance request management URLs
"""

from django.urls import path
from . import views

app_name = 'maintenance'

urlpatterns = [
    # Maintenance Request URLs
    path('', views.maintenance_request_list, name='maintenance_request_list'),
    path('create/', views.maintenance_request_create, name='maintenance_request_create'),
    path('<uuid:pk>/', views.maintenance_request_detail, name='maintenance_request_detail'),
    path('<uuid:pk>/edit/', views.maintenance_request_update, name='maintenance_request_update'),
    path('<uuid:pk>/delete/', views.maintenance_request_delete, name='maintenance_request_delete'),
    path('<uuid:pk>/assign/', views.maintenance_request_assign, name='maintenance_request_assign'),
    path('<uuid:pk>/schedule/', views.maintenance_request_schedule, name='maintenance_request_schedule'),
    path('<uuid:pk>/complete/', views.maintenance_request_complete, name='maintenance_request_complete'),
    path('<uuid:pk>/cancel/', views.maintenance_request_cancel, name='maintenance_request_cancel'),

    # Tenant-specific maintenance views
    path('tenant/<uuid:tenant_pk>/', views.tenant_maintenance_requests, name='tenant_maintenance_requests'),
]
