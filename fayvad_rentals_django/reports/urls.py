"""
Reports URLs
"""

from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # Report management
    path('', views.report_list, name='report_list'),
    path('generate/<str:report_type>/', views.report_generate, name='report_generate'),
    path('download/<uuid:report_id>/', views.report_download, name='report_download'),

    # API endpoints for report generation
    path('api/generate/', views.api_generate_report, name='api_generate_report'),
]
