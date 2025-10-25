"""
Payment management URLs
"""

from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Payment URLs
    path('', views.payment_list, name='payment_list'),
    path('create/', views.payment_create, name='payment_create'),
    path('<uuid:pk>/', views.payment_detail, name='payment_detail'),
    path('<uuid:pk>/edit/', views.payment_update, name='payment_update'),
    path('<uuid:pk>/delete/', views.payment_delete, name='payment_delete'),
    path('<uuid:pk>/complete/', views.payment_complete, name='payment_complete'),
    path('<uuid:pk>/fail/', views.payment_fail, name='payment_fail'),
    path('<uuid:pk>/refund/', views.payment_refund, name='payment_refund'),
    
    # Tenant-specific payment views
    path('tenant/<uuid:tenant_pk>/', views.tenant_payments, name='tenant_payments'),
]
