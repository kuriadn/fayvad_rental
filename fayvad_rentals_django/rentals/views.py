"""
Rental agreement management views
Contract management between tenants and properties
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.urls import reverse
from django.utils import timezone
from .models import RentalAgreement, AgreementStatus
from .forms import RentalAgreementForm

@login_required
def rental_agreement_list(request):
    """List all rental agreements"""
    agreements = RentalAgreement.objects.select_related('tenant', 'room__location').all()

    # Filters
    status_filter = request.GET.get('status', '')
    tenant_filter = request.GET.get('tenant', '')
    room_filter = request.GET.get('room', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    if status_filter:
        agreements = agreements.filter(status=status_filter)
    if tenant_filter:
        agreements = agreements.filter(tenant_id=tenant_filter)
    if room_filter:
        agreements = agreements.filter(room_id=room_filter)
    if date_from:
        agreements = agreements.filter(start_date__gte=date_from)
    if date_to:
        agreements = agreements.filter(end_date__lte=date_to)

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        agreements = agreements.filter(
            Q(agreement_number__icontains=search_query) |
            Q(tenant__name__icontains=search_query) |
            Q(tenant__email__icontains=search_query) |
            Q(room__room_number__icontains=search_query) |
            Q(room__location__name__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(agreements, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get filter options
    tenants = agreements.values_list('tenant', flat=True).distinct()
    from tenants.models import Tenant
    available_tenants = Tenant.objects.filter(id__in=tenants).order_by('name')

    rooms = agreements.values_list('room', flat=True).distinct()
    from properties.models import Room
    available_rooms = Room.objects.filter(id__in=rooms).order_by('location__name', 'room_number')

    # Statistics
    total_agreements = agreements.count()
    active_agreements = agreements.filter(status='active').count()
    draft_agreements = agreements.filter(status='draft').count()
    expired_agreements = agreements.filter(status='expired').count()

    context = {
        'page_title': 'Rental Agreements',
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'tenant_filter': tenant_filter,
        'room_filter': room_filter,
        'date_from': date_from,
        'date_to': date_to,
        'available_tenants': available_tenants,
        'available_rooms': available_rooms,
        'agreement_statuses': AgreementStatus.choices,
        'total_agreements': total_agreements,
        'active_agreements': active_agreements,
        'draft_agreements': draft_agreements,
        'expired_agreements': expired_agreements,
    }
    return render(request, 'rentals/rental_agreement_list.html', context)

@login_required
def rental_agreement_detail(request, pk):
    """View rental agreement details"""
    agreement = get_object_or_404(
        RentalAgreement.objects.select_related('tenant', 'room__location'),
        pk=pk
    )

    # Get related payments
    payments = agreement.payments.select_related('tenant').order_by('-created_at')[:10]

    context = {
        'page_title': f'Agreement: {agreement.agreement_number}',
        'agreement': agreement,
        'payments': payments,
        'payment_count': agreement.payments.count(),
    }
    return render(request, 'rentals/rental_agreement_detail.html', context)

@login_required
def rental_agreement_create(request):
    """Create new rental agreement"""
    if request.method == 'POST':
        form = RentalAgreementForm(request.POST)
        if form.is_valid():
            agreement = form.save()
            messages.success(request, f'Rental agreement "{agreement.agreement_number}" created successfully.')
            return redirect('rentals:rental_agreement_detail', pk=agreement.pk)
    else:
        form = RentalAgreementForm()

    context = {
        'page_title': 'Create Rental Agreement',
        'form': form,
    }
    return render(request, 'rentals/rental_agreement_form.html', context)

@login_required
def rental_agreement_update(request, pk):
    """Update existing rental agreement"""
    agreement = get_object_or_404(RentalAgreement, pk=pk)

    if request.method == 'POST':
        form = RentalAgreementForm(request.POST, instance=agreement)
        if form.is_valid():
            agreement = form.save()
            messages.success(request, f'Rental agreement "{agreement.agreement_number}" updated successfully.')
            return redirect('rentals:rental_agreement_detail', pk=agreement.pk)
    else:
        form = RentalAgreementForm(instance=agreement)

    context = {
        'page_title': f'Edit Agreement: {agreement.agreement_number}',
        'form': form,
        'agreement': agreement,
    }
    return render(request, 'rentals/rental_agreement_form.html', context)

@login_required
def rental_agreement_delete(request, pk):
    """Delete rental agreement"""
    agreement = get_object_or_404(RentalAgreement, pk=pk)

    if request.method == 'POST':
        agreement_number = agreement.agreement_number
        agreement.delete()
        messages.success(request, f'Rental agreement "{agreement_number}" deleted successfully.')
        return redirect('rentals:rental_agreement_list')

    context = {
        'page_title': f'Delete Agreement: {agreement.agreement_number}',
        'object': agreement,
        'object_name': 'rental agreement',
        'cancel_url': reverse('rentals:rental_agreement_detail', kwargs={'pk': pk}),
    }
    return render(request, 'rentals/rental_agreement_confirm_delete.html', context)

@login_required
def rental_agreement_activate(request, pk):
    """Activate a rental agreement"""
    agreement = get_object_or_404(RentalAgreement, pk=pk)

    if agreement.status != AgreementStatus.DRAFT:
        messages.error(request, f'Agreement {agreement.agreement_number} is not in draft status.')
        return redirect('rentals:rental_agreement_detail', pk=pk)

    if request.method == 'POST':
        agreement.activate_agreement()
        messages.success(request, f'Rental agreement "{agreement.agreement_number}" activated successfully.')
        return redirect('rentals:rental_agreement_detail', pk=pk)

    context = {
        'page_title': f'Activate Agreement: {agreement.agreement_number}',
        'agreement': agreement,
        'action': 'activate',
    }
    return render(request, 'rentals/rental_agreement_action.html', context)

@login_required
def rental_agreement_terminate(request, pk):
    """Terminate a rental agreement"""
    agreement = get_object_or_404(RentalAgreement, pk=pk)

    if not agreement.can_be_terminated:
        messages.error(request, f'Agreement {agreement.agreement_number} cannot be terminated.')
        return redirect('rentals:rental_agreement_detail', pk=pk)

    if request.method == 'POST':
        from datetime import date
        termination_date = request.POST.get('termination_date', '').strip()
        if termination_date:
            termination_date = date.fromisoformat(termination_date)
        else:
            termination_date = None

        agreement.terminate_agreement(termination_date)
        messages.success(request, f'Rental agreement "{agreement.agreement_number}" terminated successfully.')
        return redirect('rentals:rental_agreement_detail', pk=pk)

    context = {
        'page_title': f'Terminate Agreement: {agreement.agreement_number}',
        'agreement': agreement,
        'action': 'terminate',
    }
    return render(request, 'rentals/rental_agreement_action.html', context)

@login_required
def rental_agreement_give_notice(request, pk):
    """Give notice for agreement termination"""
    agreement = get_object_or_404(RentalAgreement, pk=pk)

    if agreement.status != AgreementStatus.ACTIVE:
        messages.error(request, f'Agreement {agreement.agreement_number} is not active.')
        return redirect('rentals:rental_agreement_detail', pk=pk)

    if request.method == 'POST':
        from datetime import date
        notice_date = request.POST.get('notice_date', '').strip()
        if notice_date:
            notice_date = date.fromisoformat(notice_date)
        else:
            notice_date = date.today()

        agreement.give_notice(notice_date)
        messages.success(request, f'Notice given for agreement "{agreement.agreement_number}".')
        return redirect('rentals:rental_agreement_detail', pk=pk)

    context = {
        'page_title': f'Give Notice: {agreement.agreement_number}',
        'agreement': agreement,
        'action': 'give_notice',
    }
    return render(request, 'rentals/rental_agreement_action.html', context)

@login_required
def tenant_agreements(request, tenant_pk):
    """View rental agreements for a specific tenant"""
    from tenants.models import Tenant
    tenant = get_object_or_404(Tenant, pk=tenant_pk)

    agreements = RentalAgreement.objects.filter(
        tenant=tenant
    ).select_related('room__location').order_by('-start_date')

    context = {
        'page_title': f'Agreements - {tenant.name}',
        'tenant': tenant,
        'agreements': agreements,
        'agreement_count': agreements.count(),
        'active_agreement': agreements.filter(status='active').first(),
    }
    return render(request, 'rentals/tenant_agreements.html', context)
