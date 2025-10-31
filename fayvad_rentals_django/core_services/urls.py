"""
Simple workflow API URLs
Provides basic state transition endpoints
"""

from django.urls import path
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .workflow_service import SimpleWorkflowService
import json

app_name = 'core_services'

@login_required
@require_http_methods(["POST"])
@csrf_exempt
def workflow_transition_api(request, model_type, instance_id):
    """
    Simple workflow state transition API - Staff/Admin only
    POST /api/workflows/transition/{model_type}/{instance_id}/
    Body: {"new_status": "completed", "notes": "Optional notes"}
    """
    # Security check: Prevent tenant users from performing workflow transitions
    if hasattr(request.user, 'tenant_profile') and request.user.tenant_profile:
        return JsonResponse({
            'success': False,
            'error': 'Access denied'
        }, status=403)

    try:
        # Handle both JSON and form data
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            new_status = data.get('new_status')
            notes = data.get('notes', '')
        else:
            # Handle form data
            new_status = request.POST.get('new_status')
            notes = request.POST.get('notes', '')

        if not new_status:
            return JsonResponse({
                'success': False,
                'error': 'new_status is required'
            }, status=400)

        # Get the model instance (case-insensitive)
        instance = None
        model_type_lower = model_type.lower()
        if model_type_lower == 'maintenance':
            from maintenance.models import MaintenanceRequest
            instance = MaintenanceRequest.objects.get(id=instance_id)
        elif model_type_lower == 'payment':
            from payments.models import Payment
            instance = Payment.objects.get(id=instance_id)
        elif model_type_lower == 'rental':
            from rentals.models import RentalAgreement
            instance = RentalAgreement.objects.get(id=instance_id)
        elif model_type_lower == 'complaint':
            from tenants.models import Complaint
            instance = Complaint.objects.get(id=instance_id)
        else:
            return JsonResponse({
                'success': False,
                'error': f'Unsupported model type: {model_type}'
            }, status=400)

        # Perform the transition
        result = SimpleWorkflowService.transition_state(instance, new_status, request.user, notes)

        # For form submissions (not AJAX), redirect back to the detail page
        if request.content_type != 'application/json':
            from django.contrib import messages
            from django.shortcuts import redirect

            if result['success']:
                messages.success(request, f'Status changed from {result["old_status"]} to {result["new_status"]}')
                return redirect(request.META.get('HTTP_REFERER', '/'))
            else:
                messages.error(request, result['error'])
                return redirect(request.META.get('HTTP_REFERER', '/'))

        # For AJAX requests, return JSON
        if result['success']:
            return JsonResponse({
                'success': True,
                'message': f'Status changed from {result["old_status"]} to {result["new_status"]}',
                'data': result
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result['error']
            }, status=400)
        # Perform the transition
        result = SimpleWorkflowService.transition_state(instance, new_status, request.user, notes)

        # For form submissions (not AJAX), redirect back to the detail page
        if request.content_type != 'application/json':
            from django.contrib import messages
            from django.shortcuts import redirect
            
            if result['success']:
                messages.success(request, f'Status changed from {result["old_status"]} to {result["new_status"]}')
                # Redirect back to the referring page
                return redirect(request.META.get('HTTP_REFERER', '/'))
            else:
                messages.error(request, result['error'])
                return redirect(request.META.get('HTTP_REFERER', '/'))

        # For AJAX requests, return JSON
        if result['success']:
            return JsonResponse({
                'success': True,
                'message': f'Status changed from {result["old_status"]} to {result["new_status"]}',
                'data': result
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result['error']
            }, status=400)
        # Perform the transition
        result = SimpleWorkflowService.transition_state(instance, new_status, request.user, notes)

        # For form submissions (not AJAX), redirect back to the detail page
        if request.content_type != 'application/json':
            from django.contrib import messages
            from django.shortcuts import redirect
            
            if result['success']:
                messages.success(request, f'Status changed from {result["old_status"]} to {result["new_status"]}')
                # Redirect back to the referring page
                return redirect(request.META.get('HTTP_REFERER', '/'))
            else:
                messages.error(request, result['error'])
                return redirect(request.META.get('HTTP_REFERER', '/'))

        # For AJAX requests, return JSON
        if result['success']:
            return JsonResponse({
                'success': True,
                'message': f'Status changed from {result["old_status"]} to {result["new_status"]}',
                'data': result
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result['error']
            }, status=400)
        # Perform the transition
        result = SimpleWorkflowService.transition_state(instance, new_status, request.user, notes)

        # For form submissions (not AJAX), redirect back to the detail page
        if request.content_type != 'application/json':
            from django.contrib import messages
            from django.shortcuts import redirect
            
            if result['success']:
                messages.success(request, f'Status changed from {result["old_status"]} to {result["new_status"]}')
                # Redirect back to the referring page
                return redirect(request.META.get('HTTP_REFERER', '/'))
            else:
                messages.error(request, result['error'])
                return redirect(request.META.get('HTTP_REFERER', '/'))

        # For AJAX requests, return JSON
        if result['success']:
            return JsonResponse({
                'success': True,
                'message': f'Status changed from {result["old_status"]} to {result["new_status"]}',
                'data': result
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result['error']
            }, status=400)
        # Perform the transition
        result = SimpleWorkflowService.transition_state(instance, new_status, request.user, notes)

        # For form submissions (not AJAX), redirect back to the detail page
        if request.content_type != 'application/json':
            from django.contrib import messages
            from django.shortcuts import redirect
            
            if result['success']:
                messages.success(request, f'Status changed from {result["old_status"]} to {result["new_status"]}')
                # Redirect back to the referring page
                return redirect(request.META.get('HTTP_REFERER', '/'))
            else:
                messages.error(request, result['error'])
                return redirect(request.META.get('HTTP_REFERER', '/'))

        # For AJAX requests, return JSON
        if result['success']:
            return JsonResponse({
                'success': True,
                'message': f'Status changed from {result["old_status"]} to {result["new_status"]}',
                'data': result
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result['error']
            }, status=400)

    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in workflow transition: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

urlpatterns = [
    # Simple workflow transitions
    path('transition/<str:model_type>/<str:instance_id>/', workflow_transition_api, name='workflow_transition'),
]
