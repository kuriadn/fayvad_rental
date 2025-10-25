"""
Context Processors for Django Templates
Simple health and status information - Pure Django
"""

from django.db import connection
from django.core.cache import cache
from datetime import datetime


def system_context(request):
    """
    Provide system health and status context to all templates
    Pure Django implementation - no external dependencies
    """
    try:
        # Check database connectivity
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = "operational"
    except Exception:
        db_status = "error"

    # Check cache connectivity
    try:
        cache.set('health_check', 'ok', 1)
        cache_status = "operational" if cache.get('health_check') == 'ok' else "error"
    except Exception:
        cache_status = "error"

    # Overall system status
    overall_status = "healthy" if db_status == "operational" and cache_status == "operational" else "degraded"

    health = {
        "status": overall_status,
        "overall_status": overall_status,
        "timestamp": datetime.now().isoformat(),
        "services": {
            "django": {"status": "operational"},
            "database": {"status": db_status},
            "cache": {"status": cache_status},
        }
    }

    # System information
    system_info = {
        'app_name': 'Fayvad Rentals',
        'version': '1.0.0',
        'environment': 'production',  # Can be dynamic from settings
    }

    context = {
        'system_health': health,
        'system_info': system_info,
        'system_available': True,
    }

    return context

