"""
URL configuration for fayvad_rentals project.

Pure Django rental management system
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect, render
from tenants import views as tenants_views

def homepage(request):
    """Marketing homepage for Fayvad Rentals"""
    return render(request, 'homepage.html', {
        'contact_info': {
            'address': 'P.O. Box 1762-00900 Kiambu',
            'phone': '0712104734',
            'email': 'services@rental.fayvad.com'
        }
    })

def health_check(request):
    """Simple health check endpoint for Docker"""
    from django.http import JsonResponse
    return JsonResponse({'status': 'healthy', 'timestamp': '2025-10-20'})

urlpatterns = [
    # Health check for Docker
    path('health/', health_check, name='health_check'),

    # Marketing homepage
    path('', homepage, name='homepage'),

    # Admin
    path("admin/", admin.site.urls),

    # Authentication
    path("accounts/", include("accounts.urls")),

    # Core rental modules
    path("tenants/", include("tenants.urls")),
    path("properties/", include("properties.urls")),
    path("payments/", include("payments.urls")),
    path("rentals/", include("rentals.urls")),
    path("maintenance/", include("maintenance.urls")),
    path("documents/", include("documents.urls")),
    path("reports/", include("reports.urls")),


    # Dashboard and BI
    path("dashboard/", include("dashboard.urls")),

    # Simple workflow API (now in core_services)
    path("api/workflows/", include("core_services.urls")),

    # Tenant portal
    path("tenant/", include("tenants.urls")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)