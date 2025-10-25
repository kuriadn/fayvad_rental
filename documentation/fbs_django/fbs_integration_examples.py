#!/usr/bin/env python3
"""
FBS Suite v4.0.0 - Integration Examples

Practical examples of embedding FBS services in Django applications.
These examples show the most common integration patterns.
"""

# ============================================================================
# EXAMPLE 1: Basic FBS Integration in Django View
# ============================================================================

from django.http import JsonResponse
from django.shortcuts import render
from fbs_django.apps.core.services import FBSInterface


def dashboard_view(request):
    """
    Basic FBS integration - embed services directly in views
    """
    # Direct FBS instantiation (no HTTP!)
    fbs = FBSInterface(solution_name="my_company")

    # Get data from multiple FBS services
    system_health = fbs.get_system_health()
    license_info = fbs.get_license_info()
    recent_documents = fbs.dms.list_documents(limit=5)

    context = {
        'health': system_health,
        'license': license_info,
        'documents': recent_documents,
    }

    return render(request, 'dashboard.html', context)


# ============================================================================
# EXAMPLE 2: Service-Specific Operations
# ============================================================================

def document_upload_view(request):
    """
    Document management with FBS DMS service
    """
    if request.method == 'POST':
        fbs = FBSInterface("my_company")

        # Direct DMS service call
        result = fbs.dms.create_document(
            document_data={
                'name': request.POST['name'],
                'title': request.POST['title'],
                'description': request.POST.get('description'),
            },
            created_by=str(request.user.id),
            file_obj=request.FILES.get('file')
        )

        if result['success']:
            return JsonResponse({'message': 'Document uploaded', 'id': result['document_id']})
        else:
            return JsonResponse({'error': result['error']}, status=400)

    return render(request, 'upload.html')


# ============================================================================
# EXAMPLE 3: Business Logic Integration
# ============================================================================

class BusinessService:
    """
    Your business logic layer integrating FBS services
    """

    def __init__(self, solution_name: str):
        # Embed FBS directly
        self.fbs = FBSInterface(solution_name)

    def create_customer_profile(self, customer_data: dict) -> dict:
        """
        Create customer with FBS integrations
        """
        # Use FBS MSME service for business logic
        business_result = self.fbs.msme.create_business_profile(customer_data)

        # Use FBS DMS for document management
        if customer_data.get('documents'):
            for doc in customer_data['documents']:
                self.fbs.dms.create_document(doc, created_by=customer_data['user_id'])

        # Use FBS compliance for regulatory checks
        compliance_result = self.fbs.compliance.check_business_compliance(business_result['id'])

        return {
            'business': business_result,
            'compliance': compliance_result,
            'status': 'created'
        }


# Django view using the service
def create_customer_view(request):
    """
    Customer creation with integrated FBS services
    """
    service = BusinessService("my_company")

    result = service.create_customer_profile({
        'name': request.POST['name'],
        'type': request.POST['type'],
        'documents': request.FILES.getlist('documents'),
        'user_id': str(request.user.id),
    })

    return JsonResponse(result)


# ============================================================================
# EXAMPLE 4: Workflow Integration
# ============================================================================

def process_loan_application(request):
    """
    End-to-end loan processing with FBS workflow integration
    """
    fbs = FBSInterface("bank_solution")

    # Start FBS workflow for loan processing
    workflow_result = fbs.workflows.start_workflow(
        workflow_definition_id="loan_approval",
        initial_data={
            'applicant': request.POST['applicant_id'],
            'amount': request.POST['amount'],
            'documents': [doc.id for doc in request.FILES.getlist('documents')],
        }
    )

    # Create audit trail
    fbs.audit.create_entry({
        'action': 'loan_application_started',
        'resource_type': 'workflow',
        'resource_id': workflow_result['workflow_id'],
        'user_id': str(request.user.id),
    })

    # Send notification
    fbs.notifications.send_alert({
        'type': 'loan_application',
        'recipient': request.user.email,
        'workflow_id': workflow_result['workflow_id'],
    })

    return JsonResponse(workflow_result)


# ============================================================================
# EXAMPLE 5: API Integration Pattern
# ============================================================================

from rest_framework.views import APIView
from rest_framework.response import Response
from fbs_django.apps.core.permissions import FBSLicensePermission


class BusinessAnalyticsAPI(APIView):
    """
    REST API view with FBS BI integration
    """
    permission_classes = [FBSLicensePermission]

    def get(self, request):
        # FBS automatically checks license permissions
        fbs = FBSInterface("my_company")

        # Get analytics from FBS BI service
        analytics = fbs.bi.get_business_analytics(
            date_from=request.GET.get('from'),
            date_to=request.GET.get('to'),
            metrics=request.GET.getlist('metrics')
        )

        return Response(analytics)


# ============================================================================
# EXAMPLE 6: Background Task Integration
# ============================================================================

from django.core.management.base import BaseCommand


class FBSDataSyncCommand(BaseCommand):
    """
    Management command using FBS for data synchronization
    """

    def handle(self, *args, **options):
        fbs = FBSInterface("my_company")

        # Sync data with external systems
        odoo_sync = fbs.odoo.sync_customers()
        bi_update = fbs.bi.update_dashboards()

        self.stdout.write(
            self.style.SUCCESS(
                f'Synced {odoo_sync["customers_synced"]} customers, '
                f'updated {bi_update["dashboards_updated"]} dashboards'
            )
        )


# ============================================================================
# EXAMPLE 7: Multi-Tenant Context Management
# ============================================================================

from fbs_django.apps.core.middleware.database_router import set_current_solution


def tenant_specific_operation(request, tenant_id: str):
    """
    Operations scoped to specific tenants
    """
    # Set database context for this tenant
    set_current_solution(tenant_id)

    # FBS operations now automatically use correct database
    fbs = FBSInterface(tenant_id)

    # All operations are tenant-isolated
    documents = fbs.dms.list_documents()
    workflows = fbs.workflows.get_active_workflows()

    return JsonResponse({
        'tenant': tenant_id,
        'documents': documents,
        'workflows': workflows,
    })


# ============================================================================
# EXAMPLE 8: Error Handling and Monitoring
# ============================================================================

def robust_fbs_operation(request):
    """
    Production-ready FBS operation with comprehensive error handling
    """
    try:
        fbs = FBSInterface("my_company")

        # Operation that might fail
        result = fbs.some_business_operation(request.POST)

        # Log successful operation
        fbs.audit.create_entry({
            'action': 'operation_success',
            'user_id': str(request.user.id),
            'result': result,
        })

        return JsonResponse(result)

    except ValueError as e:
        # FBS license/feature restrictions
        return JsonResponse({
            'error': 'Feature not available',
            'details': str(e)
        }, status=403)

    except ConnectionError as e:
        # External service (Odoo, Redis) issues
        # Log for monitoring
        logger.error(f"External service error: {e}")

        return JsonResponse({
            'error': 'Service temporarily unavailable',
            'retry_after': 300
        }, status=503)

    except Exception as e:
        # Unexpected errors
        logger.exception(f"FBS operation failed: {e}")

        # Create error audit trail
        try:
            fbs.audit.create_entry({
                'action': 'operation_error',
                'user_id': str(request.user.id),
                'error': str(e),
            })
        except:
            pass  # Don't fail if audit fails

        return JsonResponse({
            'error': 'Operation failed',
            'support_id': generate_support_id()
        }, status=500)


# ============================================================================
# EXAMPLE 9: Caching Integration
# ============================================================================

def cached_analytics_view(request):
    """
    FBS caching integration for performance
    """
    fbs = FBSInterface("my_company")
    cache = fbs.cache

    cache_key = f"analytics_{request.user.id}_{request.GET.get('period', 'month')}"

    # Try cache first
    analytics = cache.get(cache_key)

    if not analytics:
        # Generate fresh analytics
        analytics = fbs.bi.generate_analytics(
            user_id=str(request.user.id),
            period=request.GET.get('period', 'month')
        )

        # Cache for 1 hour
        cache.set(cache_key, analytics, 3600)

    return JsonResponse(analytics)


# ============================================================================
# EXAMPLE 10: FBS Health Monitoring
# ============================================================================

def system_status_view(request):
    """
    System health dashboard using FBS monitoring
    """
    fbs = FBSInterface("my_company")

    # Get comprehensive system health
    health = fbs.get_system_health()

    # Check individual service status
    services_status = health.get('services', {})

    # Custom health checks
    custom_checks = {
        'database': check_database_connectivity(),
        'external_apis': check_external_services(),
    }

    return render(request, 'system_status.html', {
        'fbs_health': health,
        'services': services_status,
        'custom_checks': custom_checks,
        'overall_status': 'healthy' if all(
            service.get('status') == 'operational'
            for service in services_status.values()
        ) else 'degraded'
    })


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def check_database_connectivity():
    """Custom database health check"""
    try:
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        return {'status': 'healthy', 'response_time': '10ms'}
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}


def check_external_services():
    """Custom external service health check"""
    # Implement your external service checks
    return {'status': 'healthy', 'services_checked': 3}


def generate_support_id():
    """Generate unique support ticket ID"""
    import uuid
    return str(uuid.uuid4())[:8].upper()


# ============================================================================
# INTEGRATION SUMMARY
# ============================================================================

"""
FBS Integration Patterns Summary:

1. DIRECT EMBEDDING: Import FBSInterface directly in views/services
   - No HTTP calls, direct method invocation
   - Zero overhead, maximum performance
   - Lazy loading of services

2. SERVICE COMPOSITION: Chain multiple FBS services in business logic
   - DMS + Workflows + Notifications for document processing
   - MSME + Compliance + Accounting for business operations
   - BI + Caching for analytics

3. CONTEXT MANAGEMENT: Set solution context for multi-tenancy
   - Automatic database routing
   - Tenant data isolation
   - License validation per solution

4. ERROR HANDLING: Comprehensive error management
   - License/feature restrictions
   - External service failures
   - Audit trail for all operations

5. PERFORMANCE: Built-in optimization
   - Caching integration
   - Connection pooling
   - Lazy service loading

6. MONITORING: Health checks and observability
   - System health endpoints
   - Service status monitoring
   - Audit logging

This approach provides enterprise-grade functionality with minimal integration effort.
"""
