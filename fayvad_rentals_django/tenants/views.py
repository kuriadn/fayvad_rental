"""
Tenant views - Pure Django Implementation
Refactored to use core_services instead of FBS
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Sum

from .models import Tenant, TenantStatus
from .forms import TenantForm, TenantSearchForm, TenantOnboardingForm
from core_services import TenantService

# Initialize service
tenant_service = TenantService()


@login_required
def tenant_list(request):
    """
    List tenants - Staff/Admin only
    """
    # Security check: Prevent tenant users from accessing tenant management
    if hasattr(request.user, 'tenant_profile') and request.user.tenant_profile:
        messages.error(request, 'Access denied. You can only access your own profile.')
        return redirect('tenants:tenant_dashboard', tenant_id=request.user.tenant_profile.id)
    # Get search form
    search_form = TenantSearchForm(request.GET)

    filters = {}
    if search_form.is_valid():
        search = search_form.cleaned_data.get('search')
        if search:
            filters['search'] = search

        tenant_status = search_form.cleaned_data.get('tenant_status')
        if tenant_status:
            filters['status'] = tenant_status

        tenant_type = search_form.cleaned_data.get('tenant_type')
        if tenant_type:
            filters['type'] = tenant_type

        compliance_status = search_form.cleaned_data.get('compliance_status')
        if compliance_status:
            filters['compliance_status'] = compliance_status

    # Get page number
    page = int(request.GET.get('page', 1))

    # Get tenants from service
    result = tenant_service.get_tenants(filters=filters, page=page, page_size=20)

    if result['success']:
        context = {
            'tenants': result['data'],
            'search_form': search_form,
            'page_title': 'Tenant Management',
            'total_count': result['total'],
            'page': result['page'],
            'pages': result.get('pages', 1),
            'can_delete_tenants': request.user.groups.filter(name__in=['Manager', 'Admin']).exists(),
        }
    else:
        messages.error(request, f"Error: {result.get('error', 'Failed to load tenants')}")
        context = {
            'tenants': [],
            'search_form': search_form,
            'page_title': 'Tenant Management',
            'total_count': 0,
            'can_delete_tenants': request.user.groups.filter(name__in=['Manager', 'Admin']).exists(),
        }

    return render(request, 'tenants/tenant_list.html', context)


@login_required
def tenant_detail(request, tenant_id):
    """
    View tenant details - Pure Django implementation
    """
    # Authorization check: users can only view their own tenant profile
    # Staff/Admin and Superusers can view all tenant profiles
    if not (request.user.is_superuser or request.user.groups.filter(name__in=['Manager', 'Admin', 'Staff']).exists()):
        # Check if this user has a tenant profile and if it matches the requested tenant_id
        try:
            user_tenant_profile = request.user.tenant_profile
            if str(user_tenant_profile.id) != str(tenant_id):
                messages.error(request, "You don't have permission to view this tenant's information.")
                return redirect('tenants:tenant_dashboard', tenant_id=user_tenant_profile.id)
        except:
            # User doesn't have a tenant profile, redirect to login
            messages.error(request, "Access denied. Please contact support.")
            return redirect('accounts:login')

    result = tenant_service.get_tenant(tenant_id)

    if result['success']:
        tenant_data = result['data']

        context = {
            'tenant': tenant_data,
            'page_title': f'Tenant: {tenant_data.get("name", "Unknown")}',
            'can_delete_tenants': request.user.groups.filter(name__in=['Manager', 'Admin']).exists(),
            'is_own_profile': (
                not request.user.groups.filter(name__in=['Manager', 'Admin', 'Staff']).exists() and
                hasattr(request.user, 'tenant_profile') and
                str(request.user.tenant_profile.id) == str(tenant_id)
            ),
        }

        return render(request, 'tenants/tenant_detail.html', context)
    else:
        messages.error(request, f"Error: {result.get('error', 'Tenant not found')}")
        return redirect('tenants:tenant_list')


@login_required
def tenant_create(request):
    """
    Create new tenant - Staff/Admin only
    """
    # Security check: Prevent tenant users from creating tenants
    if hasattr(request.user, 'tenant_profile') and request.user.tenant_profile:
        messages.error(request, 'Access denied. You cannot create new tenants.')
        return redirect('tenants:tenant_dashboard', tenant_id=request.user.tenant_profile.id)
    if request.method == 'POST':
        form = TenantForm(request.POST)
        if form.is_valid():
            result = tenant_service.create_tenant(form.cleaned_data)

            if result['success']:
                tenant_data = result['data']
                messages.success(request, f"Tenant '{tenant_data['name']}' created successfully.")
                return redirect('tenants:tenant_detail', tenant_id=tenant_data['id'])
            else:
                messages.error(request, f"Error: {result.get('error', 'Failed to create tenant')}")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = TenantForm()

    return render(request, 'tenants/tenant_form.html', {
        'form': form,
        'page_title': 'Create Tenant',
        'submit_button': 'Create Tenant'
    })


@login_required
def tenant_update(request, tenant_id):
    """
    Update tenant information - Pure Django implementation
    """
    # Authorization check: users can only update their own tenant profile
    # Staff/Admin and Superusers can update all tenant profiles
    if not (request.user.is_superuser or request.user.groups.filter(name__in=['Manager', 'Admin', 'Staff']).exists()):
        # Check if this user has a tenant profile and if it matches the requested tenant_id
        try:
            user_tenant_profile = request.user.tenant_profile
            if str(user_tenant_profile.id) != str(tenant_id):
                messages.error(request, "You don't have permission to edit this tenant's information.")
                return redirect('tenants:tenant_dashboard', tenant_id=user_tenant_profile.id)
        except:
            # User doesn't have a tenant profile, redirect to login
            messages.error(request, "Access denied. Please contact support.")
            return redirect('accounts:login')

    tenant = get_object_or_404(Tenant, id=tenant_id)

    if request.method == 'POST':
        form = TenantForm(request.POST, instance=tenant)
        if form.is_valid():
            result = tenant_service.update_tenant(tenant_id, form.cleaned_data)

            if result['success']:
                messages.success(request, f"Tenant '{form.cleaned_data['name']}' updated successfully.")
                return redirect('tenants:tenant_detail', tenant_id=tenant_id)
            else:
                messages.error(request, f"Error: {result.get('error', 'Failed to update tenant')}")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = TenantForm(instance=tenant)

    return render(request, 'tenants/tenant_form.html', {
        'form': form,
        'tenant': tenant,
        'page_title': f'Update Tenant: {tenant.name}',
        'submit_button': 'Update Tenant'
    })


@login_required
def tenant_delete(request, tenant_id):
    """
    Delete tenant - Pure Django implementation
    """
    # Check permissions
    if not request.user.groups.filter(name__in=['Manager', 'Admin']).exists():
        messages.error(request, 'You do not have permission to delete tenants.')
        return redirect('tenants:tenant_detail', tenant_id=tenant_id)

    if request.method == 'POST':
        # Delete tenant
        result = tenant_service.delete_tenant(tenant_id)

        if result['success']:
            messages.success(request, f'Tenant "{result.get("tenant_name", "Tenant")}" has been deleted successfully.')
            return redirect('tenants:tenant_list')
        else:
            messages.error(request, f"Error: {result.get('error', 'Failed to delete tenant')}")
            return redirect('tenants:tenant_detail', tenant_id=tenant_id)

    # GET request: Show confirmation page with validation
    validation_result = tenant_service.validate_tenant_deletion(tenant_id)

    if validation_result['success']:
        validation_data = validation_result['data']

        # Get tenant data
        tenant_result = tenant_service.get_tenant(tenant_id)
        tenant_data = tenant_result.get('data', {}) if tenant_result.get('success') else {}

        context = {
            'tenant': tenant_data,
            'page_title': f'Delete Tenant: {tenant_data.get("name", "Unknown")}',
            'active_agreements': validation_data.get('active_agreements', []),
            'outstanding_payments': validation_data.get('outstanding_payments', []),
            'can_delete': validation_data.get('can_delete', False),
            'warnings': validation_data.get('warnings', [])
        }

        return render(request, 'tenants/tenant_confirm_delete.html', context)
    else:
        messages.error(request, f"Error: {validation_result.get('error', 'Cannot validate tenant deletion')}")
        return redirect('tenants:tenant_detail', tenant_id=tenant_id)


@require_POST
@login_required
def tenant_status_update(request, tenant_id):
    """
    Update tenant status via AJAX - Staff/Admin only
    """
    # Security check: Prevent tenant users from updating tenant status
    if hasattr(request.user, 'tenant_profile') and request.user.tenant_profile:
        return JsonResponse({'success': False, 'error': 'Access denied'}, status=403)
    tenant = get_object_or_404(Tenant, id=tenant_id)
    new_status = request.POST.get('status')

    if new_status in dict(TenantStatus.choices):
        tenant.tenant_status = new_status
        tenant.save()
        messages.success(request, f"Tenant status updated to {tenant.get_tenant_status_display()}.")
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid status'}, status=400)


@login_required
def tenant_onboarding(request):
    """
    Tenant onboarding workflow - Staff/Admin only
    """
    # Security check: Prevent tenant users from accessing tenant onboarding
    if hasattr(request.user, 'tenant_profile') and request.user.tenant_profile:
        messages.error(request, 'Access denied. You cannot onboard new tenants.')
        return redirect('tenants:tenant_dashboard', tenant_id=request.user.tenant_profile.id)
    if request.method == 'POST':
        form = TenantOnboardingForm(request.POST)
        if form.is_valid():
            tenant = form.save()
            messages.success(request, f"Tenant onboarding started for '{tenant.name}'.")
            return redirect('tenants:tenant_detail', tenant_id=tenant.id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = TenantOnboardingForm()

    return render(request, 'tenants/tenant_onboarding.html', {
        'form': form,
        'page_title': 'Tenant Onboarding',
    })


@login_required
def tenant_dashboard(request, tenant_id):
    """
    Tenant-specific dashboard
    """
    # Authorization check: users can only view their own tenant dashboard
    # Staff/Admin and Superusers can view all tenant dashboards
    if not (request.user.is_superuser or request.user.groups.filter(name__in=['Manager', 'Admin', 'Staff']).exists()):
        # Check if this user has a tenant profile and if it matches the requested tenant_id
        try:
            user_tenant_profile = request.user.tenant_profile
            if str(user_tenant_profile.id) != str(tenant_id):
                messages.error(request, "You don't have permission to view this tenant's dashboard.")
                return redirect('tenants:tenant_dashboard', tenant_id=user_tenant_profile.id)
        except:
            # User doesn't have a tenant profile, redirect to login
            messages.error(request, "Access denied. Please contact support.")
            return redirect('accounts:login')

    tenant = get_object_or_404(Tenant, id=tenant_id)

    # Get payment information
    payments = tenant.payments.order_by('-created_at')
    payment_count = payments.count()
    recent_payments = payments[:5]  # Last 5 payments

    # Get active rental agreements
    active_agreements = tenant.rental_agreements.filter(
        status__in=['active', 'draft']
    ).select_related('room__location').order_by('-start_date')

    context = {
        'tenant': tenant,
        'page_title': f'Dashboard: {tenant.name}',
        'payment_count': payment_count,
        'recent_payments': recent_payments,
        'active_agreements': active_agreements,
    }

    return render(request, 'tenants/tenant_dashboard.html', context)


# ===== API VIEWS =====

def api_tenant_list(request):
    """
    API endpoint for tenant list
    """
    page = int(request.GET.get('page', 1))
    size = int(request.GET.get('size', 20))
    status_filter = request.GET.get('status')
    search = request.GET.get('search')

    filters = {}
    if status_filter:
        filters['status'] = status_filter
    if search:
        filters['search'] = search

    result = tenant_service.get_tenants(filters=filters, page=page, page_size=size)
    return JsonResponse(result)


def api_tenant_detail(request, tenant_id):
    """
    API endpoint for tenant detail
    """
    # Authorization check: users can only view their own tenant profile via API
    # Staff/Admin and Superusers can view all tenant profiles
    if not (request.user.is_superuser or request.user.groups.filter(name__in=['Manager', 'Admin', 'Staff']).exists()):
        # Check if this user has a tenant profile and if it matches the requested tenant_id
        try:
            user_tenant_profile = request.user.tenant_profile
            if str(user_tenant_profile.id) != str(tenant_id):
                return JsonResponse({
                    'success': False,
                    'error': 'You do not have permission to view this tenant\'s information.'
                }, status=403)
        except:
            # User doesn't have a tenant profile
            return JsonResponse({
                'success': False,
                'error': 'Access denied. Please contact support.'
            }, status=403)

    result = tenant_service.get_tenant(tenant_id)
    return JsonResponse(result)


@require_POST
def api_tenant_create(request):
    """
    API endpoint for tenant creation
    """
    import json
    try:
        data = json.loads(request.body)
        result = tenant_service.create_tenant(data)
        return JsonResponse(result)
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)


# ===== COMPLAINT VIEWS =====

@login_required
def complaint_list(request):
    """List all complaints with filtering"""
    from .models import Complaint
    from .forms import ComplaintSearchForm

    # Get search form
    search_form = ComplaintSearchForm(request.GET)

    complaints = Complaint.objects.select_related(
        'tenant', 'room__location', 'assigned_to__user'
    ).all()

    # Apply filters
    if search_form.is_valid():
        search = search_form.cleaned_data.get('search')
        if search:
            complaints = complaints.filter(
                Q(complaint_number__icontains=search) |
                Q(subject__icontains=search) |
                Q(description__icontains=search) |
                Q(tenant__name__icontains=search)
            )

        status = search_form.cleaned_data.get('status')
        if status:
            complaints = complaints.filter(status=status)

        priority = search_form.cleaned_data.get('priority')
        if priority:
            complaints = complaints.filter(priority=priority)

        category = search_form.cleaned_data.get('category')
        if category:
            complaints = complaints.filter(category=category)

        assigned_to = search_form.cleaned_data.get('assigned_to')
        if assigned_to:
            complaints = complaints.filter(assigned_to=assigned_to)

        date_from = search_form.cleaned_data.get('date_from')
        if date_from:
            complaints = complaints.filter(created_at__date__gte=date_from)

        date_to = search_form.cleaned_data.get('date_to')
        if date_to:
            complaints = complaints.filter(created_at__date__lte=date_to)

    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(complaints, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Statistics
    total_complaints = complaints.count()
    open_complaints = complaints.filter(status='open').count()
    investigating_complaints = complaints.filter(status='investigating').count()
    resolved_complaints = complaints.filter(status='resolved').count()
    overdue_complaints = sum(1 for c in complaints if c.is_overdue)

    context = {
        'page_title': 'Complaints',
        'page_obj': page_obj,
        'search_form': search_form,
        'total_complaints': total_complaints,
        'open_complaints': open_complaints,
        'investigating_complaints': investigating_complaints,
        'resolved_complaints': resolved_complaints,
        'overdue_complaints': overdue_complaints,
    }

    return render(request, 'tenants/complaint_list.html', context)


@login_required
def complaint_detail(request, pk):
    """View complaint details"""
    from .models import Complaint

    complaint = get_object_or_404(
        Complaint.objects.select_related(
            'tenant', 'room__location', 'assigned_to__user'
        ),
        pk=pk
    )

    # Get workflow status
    from workflows.complaint import ComplaintWorkflowEngine
    workflow = ComplaintWorkflowEngine(complaint)
    workflow_data = {
        'current_state': workflow.get_current_state(),
        'available_events': workflow._get_available_events(request.user),
        'metrics': workflow.get_complaint_metrics(),
        'history': workflow.get_complaint_history(),
    }

    context = {
        'page_title': f'Complaint: {complaint.complaint_number}',
        'complaint': complaint,
        'workflow_data': workflow_data,
    }

    return render(request, 'tenants/complaint_detail.html', context)


@login_required
def complaint_create(request):
    """Create new complaint"""
    from .forms import TenantComplaintForm
    from .models import Complaint

    # Check if user has tenant profile
    try:
        tenant_profile = request.user.tenant_profile
    except AttributeError:
        messages.error(request, "You must have a tenant profile to submit complaints.")
        return redirect('accounts:profile')

    if request.method == 'POST':
        form = TenantComplaintForm(request.POST, user=request.user)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.tenant = tenant_profile
            complaint.save()

            # Simple status update instead of complex workflow
            from .models import ComplaintStatus
            complaint.status = ComplaintStatus.OPEN
            complaint.save()

            messages.success(request, f'Maintenance request "{complaint.subject}" submitted successfully.')
            return redirect('maintenance:tenant_maintenance_requests', tenant_pk=tenant_profile.id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = TenantComplaintForm(user=request.user)

    context = {
        'page_title': 'Submit Complaint',
        'form': form,
    }

    return render(request, 'tenants/complaint_form.html', context)


@login_required
def complaint_update(request, pk):
    """Update complaint (staff only)"""
    from .models import Complaint
    from .forms import ComplaintUpdateForm

    complaint = get_object_or_404(Complaint, pk=pk)

    # Check permissions
    if not request.user.is_staff:
        messages.error(request, "You don't have permission to update complaints.")
        return redirect('tenants:complaint_detail', pk=pk)

    if request.method == 'POST':
        form = ComplaintUpdateForm(request.POST, instance=complaint)
        if form.is_valid():
            form.save()
            messages.success(request, f'Complaint "{complaint.subject}" updated successfully.')
            return redirect('tenants:complaint_detail', pk=pk)
    else:
        form = ComplaintUpdateForm(instance=complaint)

    context = {
        'page_title': f'Update Complaint: {complaint.complaint_number}',
        'form': form,
        'complaint': complaint,
    }

    return render(request, 'tenants/complaint_form.html', context)


# ===== TENANT COMPLAINT VIEWS =====

@login_required
def tenant_complaints(request, tenant_id):
    """List complaints for a specific tenant"""
    from .models import Complaint, Tenant

    tenant = get_object_or_404(Tenant, pk=tenant_id)

    # Check permissions - tenant can view their own, staff can view all
    if not request.user.is_staff:
        try:
            user_tenant = request.user.tenant_profile
            if str(user_tenant.id) != str(tenant_id):
                messages.error(request, "You can only view your own complaints.")
                return redirect('tenants:tenant_dashboard', tenant_id=user_tenant.id)
        except AttributeError:
            messages.error(request, "Access denied.")
            return redirect('accounts:login')

    complaints = Complaint.objects.filter(tenant=tenant).select_related(
        'room__location', 'assigned_to__user'
    ).order_by('-created_at')

    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(complaints, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_title': f'Complaints - {tenant.name}',
        'tenant': tenant,
        'page_obj': page_obj,
    }

    return render(request, 'tenants/tenant_complaints.html', context)


@login_required
def tenant_complaint_create(request):
    """Tenant submits a complaint (alternative to complaint_create)"""
    return complaint_create(request)


# ===== TENANT PAYMENT VIEWS =====

@login_required
def tenant_payments(request):
    """Tenant views their own payment history"""
    # Check if user has tenant profile
    try:
        tenant_profile = request.user.tenant_profile
    except AttributeError:
        messages.error(request, "You must have a tenant profile to view payments.")
        return redirect('accounts:profile')

    from payments.models import Payment

    # Get all payments for this tenant
    payments = Payment.objects.filter(tenant=tenant_profile).select_related(
        'rental_agreement', 'room'
    ).order_by('-payment_date')

    # Calculate summary statistics
    total_paid = payments.filter(status='completed').aggregate(
        total=Sum('amount')
    )['total'] or 0

    pending_amount = payments.filter(status='pending').aggregate(
        total=Sum('amount')
    )['total'] or 0

    failed_amount = payments.filter(status='failed').aggregate(
        total=Sum('amount')
    )['total'] or 0

    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(payments, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_title': 'My Payment History',
        'payments': payments,
        'page_obj': page_obj,
        'total_paid': total_paid,
        'pending_amount': pending_amount,
        'failed_amount': failed_amount,
        'payment_count': payments.count(),
        'completed_count': payments.filter(status='completed').count(),
        'pending_count': payments.filter(status='pending').count(),
        'failed_count': payments.filter(status='failed').count(),
    }

    return render(request, 'tenants/tenant_payments.html', context)

