"""
Payment management views
Rent collection and payment processing
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum
from django.core.paginator import Paginator
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
from .models import Payment, PaymentStatus, PaymentMethod
from .forms import PaymentForm, PaymentUpdateForm

@login_required
def payment_list(request):
    """List all payments - Staff only"""
    # Check if user is staff or has tenant profile (tenants should use tenant views)
    if hasattr(request.user, 'tenant_profile') and request.user.tenant_profile:
        # This is a tenant trying to access staff payments - redirect to tenant payments
        return redirect('tenant:payment_list')

    # Only staff/admin can access this view
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('accounts:login_staff')

    payments = Payment.objects.select_related('tenant', 'rental_agreement', 'room').all()

    # Filters
    tenant_filter = request.GET.get('tenant', '')
    status_filter = request.GET.get('status', '')
    method_filter = request.GET.get('method', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    if tenant_filter:
        payments = payments.filter(tenant_id=tenant_filter)
    if status_filter:
        payments = payments.filter(status=status_filter)
    if method_filter:
        payments = payments.filter(payment_method=method_filter)
    if date_from:
        payments = payments.filter(payment_date__gte=date_from)
    if date_to:
        payments = payments.filter(payment_date__lte=date_to)

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        payments = payments.filter(
            Q(payment_number__icontains=search_query) |
            Q(reference_number__icontains=search_query) |
            Q(transaction_id__icontains=search_query) |
            Q(tenant__name__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(payments, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Calculate totals
    total_amount = payments.aggregate(total=Sum('amount'))['total'] or 0
    completed_amount = payments.filter(status='completed').aggregate(total=Sum('amount'))['total'] or 0
    pending_amount = payments.filter(status='pending').aggregate(total=Sum('amount'))['total'] or 0

    # Get filter options
    tenants = payments.values_list('tenant', flat=True).distinct()
    from tenants.models import Tenant
    available_tenants = Tenant.objects.filter(id__in=tenants).order_by('name')

    context = {
        'page_title': 'Payments',
        'page_obj': page_obj,
        'search_query': search_query,
        'tenant_filter': tenant_filter,
        'status_filter': status_filter,
        'method_filter': method_filter,
        'date_from': date_from,
        'date_to': date_to,
        'available_tenants': available_tenants,
        'payment_statuses': PaymentStatus.choices,
        'payment_methods': PaymentMethod.choices,
        'total_count': payments.count(),
        'total_amount': total_amount,
        'completed_amount': completed_amount,
        'pending_amount': pending_amount,
    }
    return render(request, 'payments/payment_list.html', context)

@login_required
def payment_detail(request, pk):
    """View payment details - Staff only"""
    # Check if user is staff or has tenant profile (tenants should use tenant views)
    if hasattr(request.user, 'tenant_profile') and request.user.tenant_profile:
        # This is a tenant trying to access staff payment details - redirect to tenant payments
        return redirect('tenant:payment_list')

    # Only staff/admin can access this view
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('accounts:login_staff')

    payment = get_object_or_404(
        Payment.objects.select_related('tenant', 'rental_agreement', 'room'),
        pk=pk
    )

    context = {
        'page_title': f'Payment: {payment.payment_number}',
        'payment': payment,
    }
    return render(request, 'payments/payment_detail.html', context)

@login_required
def payment_create(request):
    """Create new payment - Staff only"""
    # Check if user is staff or has tenant profile (tenants should use tenant views)
    if hasattr(request.user, 'tenant_profile') and request.user.tenant_profile:
        # This is a tenant trying to access staff payment creation - redirect to tenant payment reporting
        return redirect('tenant:payment_report')

    # Only staff/admin can access this view
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('accounts:login_staff')

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save()
            messages.success(request, f'Payment "{payment.payment_number}" created successfully.')
            return redirect('payments:payment_detail', pk=payment.pk)
    else:
        form = PaymentForm()

    context = {
        'page_title': 'Create Payment',
        'form': form,
    }
    return render(request, 'payments/payment_form.html', context)

@login_required
def payment_update(request, pk):
    """Update existing payment - Staff only"""
    # Check if user is staff or has tenant profile (tenants should use tenant views)
    if hasattr(request.user, 'tenant_profile') and request.user.tenant_profile:
        # This is a tenant trying to access staff payment update - redirect to tenant payments
        return redirect('tenant:payment_list')

    # Only staff/admin can access this view
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('accounts:login_staff')

    payment = get_object_or_404(Payment, pk=pk)

    if request.method == 'POST':
        form = PaymentUpdateForm(request.POST, instance=payment)
        if form.is_valid():
            payment = form.save()
            messages.success(request, f'Payment "{payment.payment_number}" updated successfully.')
            return redirect('payments:payment_detail', pk=payment.pk)
    else:
        form = PaymentUpdateForm(instance=payment)

    context = {
        'page_title': f'Edit Payment: {payment.payment_number}',
        'form': form,
        'payment': payment,
    }
    return render(request, 'payments/payment_form.html', context)

@login_required
def payment_delete(request, pk):
    """Delete payment - Staff only"""
    # Check if user is staff or has tenant profile (tenants should use tenant views)
    if hasattr(request.user, 'tenant_profile') and request.user.tenant_profile:
        # This is a tenant trying to access staff payment delete - redirect to tenant payments
        return redirect('tenant:payment_list')

    # Only staff/admin can access this view
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('accounts:login_staff')

    payment = get_object_or_404(Payment, pk=pk)

    if request.method == 'POST':
        payment_number = payment.payment_number
        payment.delete()
        messages.success(request, f'Payment "{payment_number}" deleted successfully.')
        return redirect('payments:payment_list')

    context = {
        'page_title': f'Delete Payment: {payment.payment_number}',
        'object': payment,
        'object_name': 'payment',
        'cancel_url': reverse('payments:payment_detail', kwargs={'pk': pk}),
    }
    return render(request, 'payments/payment_confirm_delete.html', context)

@login_required
def payment_complete(request, pk):
    """Mark payment as completed"""
    payment = get_object_or_404(Payment, pk=pk)

    if payment.status != PaymentStatus.PENDING:
        messages.error(request, f'Payment {payment.payment_number} is not pending.')
        return redirect('payments:payment_detail', pk=pk)

    if request.method == 'POST':
        transaction_id = request.POST.get('transaction_id', '').strip()
        payment.complete_payment(transaction_id if transaction_id else None)
        messages.success(request, f'Payment "{payment.payment_number}" marked as completed.')
        return redirect('payments:payment_detail', pk=pk)

    context = {
        'page_title': f'Complete Payment: {payment.payment_number}',
        'payment': payment,
    }
    return render(request, 'payments/payment_complete.html', context)

@login_required
def payment_fail(request, pk):
    """Mark payment as failed"""
    payment = get_object_or_404(Payment, pk=pk)

    if payment.status != PaymentStatus.PENDING:
        messages.error(request, f'Payment {payment.payment_number} is not pending.')
        return redirect('payments:payment_detail', pk=pk)

    if request.method == 'POST':
        reason = request.POST.get('reason', '').strip()
        payment.fail_payment(reason if reason else None)
        messages.success(request, f'Payment "{payment.payment_number}" marked as failed.')
        return redirect('payments:payment_detail', pk=pk)

    context = {
        'page_title': f'Fail Payment: {payment.payment_number}',
        'payment': payment,
    }
    return render(request, 'payments/payment_fail.html', context)

@login_required
def payment_refund(request, pk):
    """Process payment refund"""
    payment = get_object_or_404(Payment, pk=pk)

    if not payment.is_refundable:
        messages.error(request, f'Payment {payment.payment_number} cannot be refunded.')
        return redirect('payments:payment_detail', pk=pk)

    if request.method == 'POST':
        try:
            refund_amount = Decimal(request.POST.get('refund_amount', '0'))
            if refund_amount <= 0 or refund_amount > payment.amount:
                raise ValueError("Invalid refund amount")

            payment.refund_payment(refund_amount if refund_amount != payment.amount else None)
            messages.success(request, f'Payment "{payment.payment_number}" refunded successfully.')
            return redirect('payments:payment_detail', pk=pk)
        except (ValueError, Decimal.InvalidOperation) as e:
            messages.error(request, f'Invalid refund amount: {e}')

    context = {
        'page_title': f'Refund Payment: {payment.payment_number}',
        'payment': payment,
    }
    return render(request, 'payments/payment_refund.html', context)

@login_required
def tenant_payments(request, tenant_pk):
    """View payments for a specific tenant"""
    from tenants.models import Tenant
    tenant = get_object_or_404(Tenant, pk=tenant_pk)

    payments = Payment.objects.filter(tenant=tenant).select_related('rental_agreement', 'room').order_by('-payment_date')

    # Calculate tenant payment summary
    total_paid = payments.filter(status='completed').aggregate(
        total=Sum('amount')
    )['total'] or 0

    pending_amount = payments.filter(status='pending').aggregate(
        total=Sum('amount')
    )['total'] or 0

    context = {
        'page_title': f'Payments - {tenant.name}',
        'tenant': tenant,
        'payments': payments,
        'total_paid': total_paid,
        'pending_amount': pending_amount,
        'payment_count': payments.count(),
    }
    return render(request, 'payments/tenant_payments.html', context)
