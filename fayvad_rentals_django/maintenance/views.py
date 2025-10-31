"""
Maintenance request management views
Property repair and maintenance workflows
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.urls import reverse
from django.utils import timezone
from .models import MaintenanceRequest, Priority, MaintenanceStatus
from .forms import (
    MaintenanceRequestForm, MaintenanceRequestUpdateForm,
    MaintenanceCompleteForm, MaintenanceAssignForm, MaintenanceScheduleForm
)

@login_required
def maintenance_request_list(request):
    """List all maintenance requests - Staff/Admin only"""
    # Security check: Prevent tenant users from accessing maintenance management
    if hasattr(request.user, 'tenant_profile') and request.user.tenant_profile:
        messages.error(request, 'Access denied. You cannot access maintenance management.')
        return redirect('tenants:tenant_dashboard', tenant_id=request.user.tenant_profile.id)
    requests = MaintenanceRequest.objects.select_related('tenant', 'room__location', 'created_by').all()

    # Filters
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    tenant_filter = request.GET.get('tenant', '')
    room_filter = request.GET.get('room', '')

    if status_filter:
        requests = requests.filter(status=status_filter)
    if priority_filter:
        requests = requests.filter(priority=priority_filter)
    if tenant_filter:
        requests = requests.filter(tenant_id=tenant_filter)
    if room_filter:
        requests = requests.filter(room_id=room_filter)

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        requests = requests.filter(
            Q(request_number__icontains=search_query) |
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(tenant__name__icontains=search_query) |
            Q(room__room_number__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(requests, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get filter options
    tenants = MaintenanceRequest.objects.values_list('tenant', flat=True).distinct()
    from tenants.models import Tenant
    available_tenants = Tenant.objects.filter(id__in=tenants).order_by('name')

    rooms = MaintenanceRequest.objects.values_list('room', flat=True).distinct()
    from properties.models import Room
    available_rooms = Room.objects.filter(id__in=rooms).order_by('location__name', 'room_number')

    # Statistics
    total_requests = requests.count()
    pending_requests = requests.filter(status='pending').count()
    in_progress_requests = requests.filter(status='in_progress').count()
    completed_requests = requests.filter(status='completed').count()

    context = {
        'page_title': 'Maintenance Requests',
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'tenant_filter': tenant_filter,
        'room_filter': room_filter,
        'available_tenants': available_tenants,
        'available_rooms': available_rooms,
        'priority_choices': Priority.choices,
        'status_choices': MaintenanceStatus.choices,
        'total_requests': total_requests,
        'pending_requests': pending_requests,
        'in_progress_requests': in_progress_requests,
        'completed_requests': completed_requests,
    }
    return render(request, 'maintenance/maintenance_request_list.html', context)

@login_required
def maintenance_request_detail(request, pk):
    """View maintenance request details"""
    maintenance_request = get_object_or_404(
        MaintenanceRequest.objects.select_related('tenant', 'room__location', 'created_by'),
        pk=pk
    )

    # Escalation history simplified - removed complex audit logging
    escalation_history = []

    context = {
        'page_title': f'Maintenance: {maintenance_request.request_number}',
        'maintenance_request': maintenance_request,
        'escalation_history': escalation_history,
    }
    return render(request, 'maintenance/maintenance_request_detail.html', context)

@login_required
def maintenance_request_create(request):
    """Create new maintenance request - Staff/Admin only"""
    # Security check: Prevent tenant users from accessing maintenance management
    if hasattr(request.user, 'tenant_profile') and request.user.tenant_profile:
        messages.error(request, 'Access denied. You cannot access maintenance management.')
        return redirect('tenants:tenant_dashboard', tenant_id=request.user.tenant_profile.id)
    if request.method == 'POST':
        form = MaintenanceRequestForm(request.POST)
        if form.is_valid():
            maintenance_request = form.save(commit=False)
            maintenance_request.created_by = request.user
            maintenance_request.save()
            messages.success(request, f'Maintenance request "{maintenance_request.request_number}" created successfully.')
            return redirect('maintenance:maintenance_request_detail', pk=maintenance_request.pk)
    else:
        form = MaintenanceRequestForm()

    context = {
        'page_title': 'Create Maintenance Request',
        'form': form,
    }
    return render(request, 'maintenance/maintenance_request_form.html', context)

@login_required
def maintenance_request_update(request, pk):
    """Update existing maintenance request - Staff/Admin only"""
    # Security check: Prevent tenant users from accessing maintenance management
    if hasattr(request.user, 'tenant_profile') and request.user.tenant_profile:
        messages.error(request, 'Access denied. You cannot access maintenance management.')
        return redirect('tenants:tenant_dashboard', tenant_id=request.user.tenant_profile.id)
    maintenance_request = get_object_or_404(MaintenanceRequest, pk=pk)

    if request.method == 'POST':
        form = MaintenanceRequestUpdateForm(request.POST, instance=maintenance_request)
        if form.is_valid():
            maintenance_request = form.save()
            messages.success(request, f'Maintenance request "{maintenance_request.request_number}" updated successfully.')
            return redirect('maintenance:maintenance_request_detail', pk=maintenance_request.pk)
    else:
        form = MaintenanceRequestUpdateForm(instance=maintenance_request)

    context = {
        'page_title': f'Edit Request: {maintenance_request.request_number}',
        'form': form,
        'maintenance_request': maintenance_request,
    }
    return render(request, 'maintenance/maintenance_request_form.html', context)

@login_required
def maintenance_request_delete(request, pk):
    """Delete maintenance request - Staff/Admin only"""
    # Security check: Prevent tenant users from accessing maintenance management
    if hasattr(request.user, 'tenant_profile') and request.user.tenant_profile:
        messages.error(request, 'Access denied. You cannot access maintenance management.')
        return redirect('tenants:tenant_dashboard', tenant_id=request.user.tenant_profile.id)
    maintenance_request = get_object_or_404(MaintenanceRequest, pk=pk)

    if request.method == 'POST':
        request_number = maintenance_request.request_number
        maintenance_request.delete()
        messages.success(request, f'Maintenance request "{request_number}" deleted successfully.')
        return redirect('maintenance:maintenance_request_list')

    context = {
        'page_title': f'Delete Request: {maintenance_request.request_number}',
        'object': maintenance_request,
        'object_name': 'maintenance request',
        'cancel_url': reverse('maintenance:maintenance_request_detail', kwargs={'pk': pk}),
    }
    return render(request, 'maintenance/maintenance_request_confirm_delete.html', context)

@login_required
def maintenance_request_assign(request, pk):
    """Assign maintenance request to technician using workflow engine"""
    maintenance_request = get_object_or_404(MaintenanceRequest, pk=pk)

    # Use workflow service to check permissions and get available actions
    from core_services.maintenance_service import MaintenanceService

    if not workflow_status['success']:
        messages.error(request, 'Unable to load workflow status.')
        return redirect('maintenance:maintenance_request_detail', pk=pk)

    # Check if assign action is available
    available_events = workflow_status['data']['available_events']
    if 'assign_technician' not in available_events:
        messages.error(request, f'Maintenance request {maintenance_request.request_number} cannot be assigned.')
        return redirect('maintenance:maintenance_request_detail', pk=pk)

    if request.method == 'POST':
        form = MaintenanceAssignForm(request.POST)
        if form.is_valid():
            technician_name = form.cleaned_data['assigned_to']

            # Use workflow service
            result = MaintenanceService.assign_technician(str(maintenance_request.id), technician_name, request.user)

            if result['success']:
                messages.success(request, result['message'])
                return redirect('maintenance:maintenance_request_detail', pk=pk)
            else:
                messages.error(request, result['error'])
    else:
        form = MaintenanceAssignForm()

    context = {
        'page_title': f'Assign Request: {maintenance_request.request_number}',
        'form': form,
        'maintenance_request': maintenance_request,
        'action': 'assign',
        'workflow_status': workflow_status['data'],
    }
    return render(request, 'maintenance/maintenance_request_action.html', context)

@login_required
def maintenance_request_schedule(request, pk):
    """Schedule maintenance request"""
    maintenance_request = get_object_or_404(MaintenanceRequest, pk=pk)

    if maintenance_request.status == MaintenanceStatus.COMPLETED:
        messages.error(request, f'Maintenance request {maintenance_request.request_number} is already completed.')
        return redirect('maintenance:maintenance_request_detail', pk=pk)

    if request.method == 'POST':
        form = MaintenanceScheduleForm(request.POST)
        if form.is_valid():
            scheduled_date = form.cleaned_data['scheduled_date']
            maintenance_request.schedule_maintenance(scheduled_date)
            messages.success(request, f'Maintenance request "{maintenance_request.request_number}" scheduled successfully.')
            return redirect('maintenance:maintenance_request_detail', pk=pk)
    else:
        form = MaintenanceScheduleForm()

    context = {
        'page_title': f'Schedule Request: {maintenance_request.request_number}',
        'form': form,
        'maintenance_request': maintenance_request,
        'action': 'schedule',
    }
    return render(request, 'maintenance/maintenance_request_action.html', context)

@login_required
def maintenance_request_complete(request, pk):
    """Complete maintenance request"""
    maintenance_request = get_object_or_404(MaintenanceRequest, pk=pk)

    if not maintenance_request.can_be_completed:
        messages.error(request, f'Maintenance request {maintenance_request.request_number} cannot be completed.')
        return redirect('maintenance:maintenance_request_detail', pk=pk)

    if request.method == 'POST':
        form = MaintenanceCompleteForm(request.POST)
        if form.is_valid():
            resolution_notes = form.cleaned_data.get('resolution_notes')
            actual_cost = form.cleaned_data.get('actual_cost')
            resolution_photos = form.cleaned_data.get('resolution_photos')
            follow_up_required = form.cleaned_data.get('follow_up_required')

            maintenance_request.complete_request(resolution_notes, actual_cost)

            if resolution_photos:
                import json
                try:
                    maintenance_request.resolution_photos = json.loads(resolution_photos)
                    maintenance_request.save()
                except json.JSONDecodeError:
                    messages.warning(request, 'Invalid photo URLs format. Photos not saved.')

            if follow_up_required:
                maintenance_request.follow_up_required = True
                maintenance_request.save()

            messages.success(request, f'Maintenance request "{maintenance_request.request_number}" completed successfully.')
            return redirect('maintenance:maintenance_request_detail', pk=pk)
    else:
        form = MaintenanceCompleteForm()

    context = {
        'page_title': f'Complete Request: {maintenance_request.request_number}',
        'form': form,
        'maintenance_request': maintenance_request,
        'action': 'complete',
    }
    return render(request, 'maintenance/maintenance_request_action.html', context)

@login_required
def maintenance_request_cancel(request, pk):
    """Cancel maintenance request"""
    maintenance_request = get_object_or_404(MaintenanceRequest, pk=pk)

    if not maintenance_request.can_be_cancelled:
        messages.error(request, f'Maintenance request {maintenance_request.request_number} cannot be cancelled.')
        return redirect('maintenance:maintenance_request_detail', pk=pk)

    if request.method == 'POST':
        maintenance_request.cancel_request()
        messages.success(request, f'Maintenance request "{maintenance_request.request_number}" cancelled successfully.')
        return redirect('maintenance:maintenance_request_detail', pk=pk)

    context = {
        'page_title': f'Cancel Request: {maintenance_request.request_number}',
        'maintenance_request': maintenance_request,
        'action': 'cancel',
    }
    return render(request, 'maintenance/maintenance_request_action.html', context)

@login_required
def tenant_maintenance_requests(request, tenant_pk):
    """View maintenance requests (complaints) for a specific tenant - Tenant can only view their own"""
    # Security check: Ensure tenant can only view their own maintenance requests
    if hasattr(request.user, 'tenant_profile') and request.user.tenant_profile:
        if str(request.user.tenant_profile.id) != str(tenant_pk):
            messages.error(request, 'Access denied. You can only view your own maintenance requests.')
            return redirect('tenants:tenant_dashboard', tenant_id=request.user.tenant_profile.id)
    # Staff can view any tenant's maintenance requests (no additional check needed)
    from tenants.models import Tenant, Complaint
    tenant = get_object_or_404(Tenant, pk=tenant_pk)

    # For tenants, show their complaints as maintenance requests
    maintenance_requests = Complaint.objects.filter(
        tenant=tenant
    ).select_related('room__location').order_by('-created_at')

    # Create a mapping for status compatibility
    for complaint in maintenance_requests:
        # Map complaint status to maintenance request status for display
        if complaint.status == 'open':
            complaint.status = 'pending'
        elif complaint.status == 'investigating':
            complaint.status = 'in_progress'
        elif complaint.status == 'resolved':
            complaint.status = 'completed'
        elif complaint.status == 'closed':
            complaint.status = 'completed'
        else:
            complaint.status = 'pending'

        # Add compatibility attributes
        complaint.request_number = complaint.complaint_number or f"COMP-{complaint.id}"
        complaint.title = complaint.subject
        complaint.created_by = None  # Complaints don't have created_by in the same way
        complaint.scheduled_date = None
        complaint.estimated_cost = None

    context = {
        'page_title': f'Maintenance - {tenant.name}',
        'tenant': tenant,
        'maintenance_requests': maintenance_requests,
        'total_requests': maintenance_requests.count(),
        'pending_requests': sum(1 for r in maintenance_requests if r.status == 'pending'),
        'completed_requests': sum(1 for r in maintenance_requests if r.status == 'completed'),
    }
    return render(request, 'maintenance/tenant_maintenance_requests.html', context)
