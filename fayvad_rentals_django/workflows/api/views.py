"""
Workflow API Views
REST endpoints for workflow management
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
import json
import logging

from core_services.workflow_service import SimpleWorkflowService
from ..services import NotificationService


@login_required
@require_http_methods(["GET"])


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def workflow_transition(request, model_type, instance_id):
    """
    Simple workflow state transition
    POST /api/workflows/transition/{model_type}/{instance_id}/
    Body: {"new_status": "completed", "notes": "Optional notes"}
    """
    logger = logging.getLogger(__name__)

    try:
        new_status = request.data.get('new_status')
        notes = request.data.get('notes', '')

        if not new_status:
            return JsonResponse({
                'success': False,
                'error': 'new_status is required'
            }, status=400)

        # Get the model instance
        instance = None
        if model_type == 'maintenance':
            from maintenance.models import MaintenanceRequest
            instance = MaintenanceRequest.objects.get(id=instance_id)
        elif model_type == 'payment':
            from payments.models import Payment
            instance = Payment.objects.get(id=instance_id)
        elif model_type == 'rental':
            from rentals.models import RentalAgreement
            instance = RentalAgreement.objects.get(id=instance_id)
        elif model_type == 'complaint':
            from tenants.models import Complaint
            instance = Complaint.objects.get(id=instance_id)
        else:
            return JsonResponse({
                'success': False,
                'error': f'Unsupported model type: {model_type}'
            }, status=400)

        # Perform the transition
        result = SimpleWorkflowService.transition_state(instance, new_status, request.user, notes)

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
        logger.error(f"Error in workflow transition: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)