"""
Tenant URLs
Preserves all FastAPI tenant endpoint functionality
"""

from django.urls import path
from . import views

app_name = 'tenants'

urlpatterns = [
    # Web views
    path('', views.tenant_list, name='tenant_list'),
    path('create/', views.tenant_create, name='tenant_create'),
    path('onboarding/', views.tenant_onboarding, name='tenant_onboarding'),
    path('<uuid:tenant_id>/', views.tenant_detail, name='tenant_detail'),
    path('<uuid:tenant_id>/update/', views.tenant_update, name='tenant_update'),
    path('<uuid:tenant_id>/delete/', views.tenant_delete, name='tenant_delete'),
    path('<uuid:tenant_id>/dashboard/', views.tenant_dashboard, name='tenant_dashboard'),
    path('<uuid:tenant_id>/status/', views.tenant_status_update, name='tenant_status_update'),

    # API endpoints (equivalent to FastAPI)
    path('api/', views.api_tenant_list, name='api_tenant_list'),
    path('api/<uuid:tenant_id>/', views.api_tenant_detail, name='api_tenant_detail'),
    path('api/create/', views.api_tenant_create, name='api_tenant_create'),

    # Complaint management
    path('complaints/', views.complaint_list, name='complaint_list'),
    path('complaints/create/', views.complaint_create, name='complaint_create'),
    path('complaints/<uuid:pk>/', views.complaint_detail, name='complaint_detail'),
    path('complaints/<uuid:pk>/update/', views.complaint_update, name='complaint_update'),

    # Tenant-specific payment views
    path('payments/', views.tenant_payments, name='tenant_payments'),

    # Tenant-specific complaint views
    path('tenant/<uuid:tenant_id>/complaints/', views.tenant_complaints, name='tenant_complaints'),
    path('tenant/complaints/create/', views.tenant_complaint_create, name='tenant_complaint_create'),
]
