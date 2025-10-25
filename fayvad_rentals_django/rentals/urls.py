"""
Rental agreement management URLs
"""

from django.urls import path
from . import views

app_name = 'rentals'

urlpatterns = [
    # Rental Agreement URLs
    path('', views.rental_agreement_list, name='rental_agreement_list'),
    path('create/', views.rental_agreement_create, name='rental_agreement_create'),
    path('<uuid:pk>/', views.rental_agreement_detail, name='rental_agreement_detail'),
    path('<uuid:pk>/edit/', views.rental_agreement_update, name='rental_agreement_update'),
    path('<uuid:pk>/delete/', views.rental_agreement_delete, name='rental_agreement_delete'),
    path('<uuid:pk>/activate/', views.rental_agreement_activate, name='rental_agreement_activate'),
    path('<uuid:pk>/terminate/', views.rental_agreement_terminate, name='rental_agreement_terminate'),
    path('<uuid:pk>/give-notice/', views.rental_agreement_give_notice, name='rental_agreement_give_notice'),

    # Tenant-specific agreement views
    path('tenant/<uuid:tenant_pk>/', views.tenant_agreements, name='tenant_agreements'),
]
