"""
Document management URLs
"""

from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    # Document URLs
    path('', views.document_list, name='document_list'),
    path('create/', views.document_create, name='document_create'),
    path('upload/', views.document_upload, name='document_upload'),
    path('<uuid:pk>/', views.document_detail, name='document_detail'),
    path('<uuid:pk>/edit/', views.document_update, name='document_update'),
    path('<uuid:pk>/delete/', views.document_delete, name='document_delete'),
    path('<uuid:pk>/download/', views.document_download, name='document_download'),
    path('<uuid:pk>/activate/', views.document_activate, name='document_activate'),
    path('<uuid:pk>/archive/', views.document_archive, name='document_archive'),

    # Tenant-specific document views
    path('tenant/<uuid:tenant_pk>/', views.tenant_documents, name='tenant_documents'),
]
