"""
Dashboard and analytics views
KPIs, metrics, and business intelligence
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import timedelta
from decimal import Decimal

@login_required
def dashboard_overview(request):
    """Main dashboard overview"""
    # Get key metrics
    metrics = {
        'total_tenants': get_tenant_metrics(),
        'total_rooms': get_room_metrics(),
        'total_payments': get_payment_metrics(),
        'total_maintenance': get_maintenance_metrics(),
        'occupancy_rate': get_occupancy_rate(),
        'monthly_revenue': get_monthly_revenue(),
        'pending_maintenance': get_pending_maintenance_count(),
        'active_agreements': get_active_agreements_count(),
    }

    # Recent activity
    recent_activity = get_recent_activity()

    # Charts data
    charts = {
        'revenue_trend': get_revenue_trend_data(),
        'occupancy_trend': get_occupancy_trend_data(),
        'maintenance_trend': get_maintenance_trend_data(),
        'tenant_status': get_tenant_status_distribution(),
    }

    # Get pending tasks for staff users
    pending_tasks = {}
    if request.user.is_staff or request.user.is_superuser:
        pending_tasks = get_pending_tasks_for_user(request.user)

    # Check if user can view audit logs (managers only)
    can_view_audit_logs = request.user.is_superuser or (
        hasattr(request.user, 'staff_profile') and
        request.user.staff_profile and
        request.user.staff_profile.role == 'manager'
    )

    context = {
        'page_title': 'Dashboard Overview',
        'metrics': metrics,
        'recent_activity': recent_activity,
        'charts': charts,
        'pending_tasks': pending_tasks,
        'can_view_audit_logs': can_view_audit_logs,
        'debug_user': {
            'username': request.user.username,
            'is_superuser': request.user.is_superuser,
            'is_staff': request.user.is_staff,
            'is_authenticated': request.user.is_authenticated,
        }
    }
    return render(request, 'dashboard/dashboard_overview.html', context)

@login_required
def dashboard_financial(request):
    """Financial dashboard"""
    financial_metrics = {
        'total_revenue': get_total_revenue(),
        'monthly_revenue': get_monthly_revenue(),
        'outstanding_payments': get_outstanding_payments(),
        'revenue_by_method': get_revenue_by_payment_method(),
        'monthly_trend': get_monthly_revenue_trend(),
        'deposit_summary': get_deposit_summary(),
    }

    financial_charts = {
        'revenue_trend': get_revenue_trend_data(),
        'payment_methods': get_payment_methods_chart(),
        'monthly_comparison': get_monthly_comparison_chart(),
    }

    context = {
        'page_title': 'Financial Dashboard',
        'metrics': financial_metrics,
        'charts': financial_charts,
    }
    return render(request, 'dashboard/dashboard_financial.html', context)

@login_required
def dashboard_occupancy(request):
    """Occupancy dashboard"""
    occupancy_metrics = {
        'total_rooms': get_room_metrics()['total'],
        'occupied_rooms': get_room_metrics()['occupied'],
        'available_rooms': get_room_metrics()['available'],
        'occupancy_rate': get_occupancy_rate(),
        'occupancy_trend': get_occupancy_trend_data(),
        'room_types_distribution': get_room_types_distribution(),
        'location_occupancy': get_location_occupancy(),
    }

    context = {
        'page_title': 'Occupancy Dashboard',
        'metrics': occupancy_metrics,
    }
    return render(request, 'dashboard/dashboard_occupancy.html', context)

@login_required
def dashboard_maintenance(request):
    """Maintenance dashboard"""
    maintenance_metrics = {
        'total_requests': get_maintenance_metrics()['total'],
        'pending_requests': get_maintenance_metrics()['pending'],
        'in_progress_requests': get_maintenance_metrics()['in_progress'],
        'completed_requests': get_maintenance_metrics()['completed'],
        'overdue_requests': get_overdue_maintenance_count(),
        'average_resolution_time': get_average_resolution_time(),
        'maintenance_by_priority': get_maintenance_by_priority(),
        'maintenance_trend': get_maintenance_trend_data(),
    }

    context = {
        'page_title': 'Maintenance Dashboard',
        'metrics': maintenance_metrics,
    }
    return render(request, 'dashboard/dashboard_maintenance.html', context)

@login_required
def dashboard_tenant(request):
    """Tenant dashboard"""
    tenant_metrics = {
        'total_tenants': get_tenant_metrics()['total'],
        'active_tenants': get_tenant_metrics()['active'],
        'prospective_tenants': get_tenant_metrics()['prospective'],
        'tenant_status_distribution': get_tenant_status_distribution(),
        'tenant_growth_trend': get_tenant_growth_trend(),
        'tenants_by_location': get_tenants_by_location(),
        'recent_tenant_activity': get_recent_tenant_activity(),
    }

    context = {
        'page_title': 'Tenant Dashboard',
        'metrics': tenant_metrics,
    }
    return render(request, 'dashboard/dashboard_tenant.html', context)

@login_required
def dashboard_property(request):
    """Property dashboard"""
    property_metrics = {
        'total_locations': get_location_metrics()['total'],
        'total_rooms': get_room_metrics()['total'],
        'location_distribution': get_location_distribution(),
        'room_utilization': get_room_utilization(),
        'property_performance': get_property_performance(),
        'maintenance_by_location': get_maintenance_by_location(),
    }

    context = {
        'page_title': 'Property Dashboard',
        'metrics': property_metrics,
    }
    return render(request, 'dashboard/dashboard_property.html', context)


# Helper functions for metrics calculation

def get_tenant_metrics():
    """Get tenant-related metrics"""
    from tenants.models import Tenant
    total = Tenant.objects.count()
    active = Tenant.objects.filter(tenant_status='active').count()
    prospective = Tenant.objects.filter(tenant_status='prospective').count()
    return {
        'total': total,
        'active': active,
        'prospective': prospective
    }

def get_room_metrics():
    """Get room-related metrics"""
    from properties.models import Room
    total = Room.objects.count()
    occupied = Room.objects.filter(status='occupied').count()
    available = Room.objects.filter(status='available').count()
    return {
        'total': total,
        'occupied': occupied,
        'available': available
    }

def get_payment_metrics():
    """Get payment-related metrics"""
    from payments.models import Payment
    total = Payment.objects.count()
    completed = Payment.objects.filter(status='completed').count()
    pending = Payment.objects.filter(status='pending').count()
    total_amount = Payment.objects.filter(status='completed').aggregate(
        total=Sum('amount')
    )['total'] or 0
    return {
        'total': total,
        'completed': completed,
        'pending': pending,
        'total_amount': float(total_amount)
    }

def get_maintenance_metrics():
    """Get maintenance-related metrics"""
    from maintenance.models import MaintenanceRequest
    total = MaintenanceRequest.objects.count()
    pending = MaintenanceRequest.objects.filter(status='pending').count()
    in_progress = MaintenanceRequest.objects.filter(status='in_progress').count()
    completed = MaintenanceRequest.objects.filter(status='completed').count()
    return {
        'total': total,
        'pending': pending,
        'in_progress': in_progress,
        'completed': completed
    }

def get_occupancy_rate():
    """Calculate current occupancy rate"""
    room_metrics = get_room_metrics()
    if room_metrics['total'] == 0:
        return 0
    return round((room_metrics['occupied'] / room_metrics['total']) * 100, 1)

def get_monthly_revenue():
    """Get current month revenue"""
    from payments.models import Payment
    today = timezone.now()
    start_of_month = today.replace(day=1)
    revenue = Payment.objects.filter(
        status='completed',
        payment_date__gte=start_of_month
    ).aggregate(total=Sum('amount'))['total'] or 0
    return float(revenue)

def get_pending_maintenance_count():
    """Get count of pending maintenance requests"""
    from maintenance.models import MaintenanceRequest
    return MaintenanceRequest.objects.filter(status='pending').count()

def get_active_agreements_count():
    """Get count of active rental agreements"""
    from rentals.models import RentalAgreement
    return RentalAgreement.objects.filter(status='active').count()

def get_recent_activity():
    """Get recent system activity"""
    activities = []

    # Recent payments
    from payments.models import Payment
    recent_payments = Payment.objects.select_related('tenant').filter(
        status='completed'
    ).order_by('-created_at')[:3]
    for payment in recent_payments:
        activities.append({
            'type': 'payment',
            'description': f"Payment of KSh {payment.amount} received from {payment.tenant.name}",
            'timestamp': payment.created_at,
            'icon': '💰'
        })

    # Recent maintenance requests
    from maintenance.models import MaintenanceRequest
    recent_maintenance = MaintenanceRequest.objects.select_related('tenant').order_by('-created_at')[:3]
    for maintenance in recent_maintenance:
        activities.append({
            'type': 'maintenance',
            'description': f"Maintenance request: {maintenance.title} for {maintenance.tenant.name}",
            'timestamp': maintenance.created_at,
            'icon': '🔧'
        })

    # Recent tenants
    from tenants.models import Tenant
    recent_tenants = Tenant.objects.order_by('-created_at')[:2]
    for tenant in recent_tenants:
        activities.append({
            'type': 'tenant',
            'description': f"New tenant: {tenant.name} registered",
            'timestamp': tenant.created_at,
            'icon': '👤'
        })

    # Sort by timestamp and return top 8
    activities.sort(key=lambda x: x['timestamp'], reverse=True)
    return activities[:8]

def get_revenue_trend_data():
    """Get revenue trend data for the last 12 months"""
    from payments.models import Payment
    data = []
    today = timezone.now()

    for i in range(11, -1, -1):
        month_start = (today - timedelta(days=30*i)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

        revenue = Payment.objects.filter(
            status='completed',
            payment_date__gte=month_start,
            payment_date__lte=month_end
        ).aggregate(total=Sum('amount'))['total'] or 0

        data.append({
            'month': month_start.strftime('%b %Y'),
            'revenue': float(revenue)
        })

    return data

def get_occupancy_trend_data():
    """Get occupancy trend data"""
    return [{
        'period': 'Current',
        'occupancy': get_occupancy_rate()
    }]

def get_maintenance_trend_data():
    """Get maintenance trend data"""
    from maintenance.models import MaintenanceRequest
    data = []
    today = timezone.now()

    for i in range(11, -1, -1):
        month_start = (today - timedelta(days=30*i)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

        count = MaintenanceRequest.objects.filter(
            requested_date__gte=month_start,
            requested_date__lte=month_end
        ).count()

        data.append({
            'month': month_start.strftime('%b %Y'),
            'requests': count
        })

    return data

def get_tenant_status_distribution():
    """Get tenant status distribution"""
    from tenants.models import Tenant
    data = Tenant.objects.values('tenant_status').annotate(
        count=Count('id')
    ).order_by('tenant_status')

    return list(data)

# Additional helper functions
def get_total_revenue():
    from payments.models import Payment
    return float(Payment.objects.filter(status='completed').aggregate(
        total=Sum('amount')
    )['total'] or 0)

def get_outstanding_payments():
    from payments.models import Payment
    return float(Payment.objects.filter(status='pending').aggregate(
        total=Sum('amount')
    )['total'] or 0)

def get_revenue_by_payment_method():
    from payments.models import Payment
    data = Payment.objects.filter(status='completed').values('payment_method').annotate(
        total=Sum('amount')
    ).order_by('-total')
    return [{'method': item['payment_method'], 'amount': float(item['total'])} for item in data]

def get_monthly_revenue_trend():
    return get_revenue_trend_data()

def get_deposit_summary():
    from rentals.models import RentalAgreement
    total_deposits = RentalAgreement.objects.filter(status='active').aggregate(
        total=Sum('deposit_amount')
    )['total'] or 0
    returned_deposits = RentalAgreement.objects.filter(
        security_deposit_returned=True
    ).aggregate(total=Sum('deposit_amount'))['total'] or 0
    return {
        'total_collected': float(total_deposits),
        'returned': float(returned_deposits),
        'outstanding': float(total_deposits - returned_deposits)
    }

def get_payment_methods_chart():
    return get_revenue_by_payment_method()

def get_monthly_comparison_chart():
    data = get_revenue_trend_data()
    if len(data) >= 2:
        current = data[-1]['revenue']
        previous = data[-2]['revenue']
        change = ((current - previous) / previous * 100) if previous > 0 else 0
        return {
            'current': current,
            'previous': previous,
            'change': round(change, 1)
        }
    return {'current': 0, 'previous': 0, 'change': 0}

def get_room_types_distribution():
    from properties.models import Room
    data = Room.objects.values('room_type').annotate(
        count=Count('id')
    ).order_by('room_type')
    return list(data)

def get_location_occupancy():
    from properties.models import Location
    data = []
    for location in Location.objects.all():
        total_rooms = location.rooms.count()
        occupied_rooms = location.rooms.filter(status='occupied').count()
        occupancy_rate = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0
        data.append({
            'location': location.name,
            'occupancy_rate': round(occupancy_rate, 1),
            'occupied': occupied_rooms,
            'total': total_rooms
        })
    return data

def get_overdue_maintenance_count():
    from maintenance.models import MaintenanceRequest
    overdue = [req for req in MaintenanceRequest.objects.filter(
        status__in=['pending', 'in_progress']
    ) if req.is_overdue]
    return len(overdue)

def get_average_resolution_time():
    from maintenance.models import MaintenanceRequest
    completed_requests = MaintenanceRequest.objects.filter(
        status='completed',
        completed_date__isnull=False
    )
    if not completed_requests.exists():
        return 0
    total_days = sum((req.completed_date - req.requested_date).days for req in completed_requests)
    return round(total_days / completed_requests.count(), 1)

def get_maintenance_by_priority():
    from maintenance.models import MaintenanceRequest
    data = MaintenanceRequest.objects.values('priority').annotate(
        count=Count('id')
    ).order_by('priority')
    return list(data)

def get_tenant_growth_trend():
    from tenants.models import Tenant
    data = []
    today = timezone.now()
    for i in range(11, -1, -1):
        month_start = (today - timedelta(days=30*i)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        count = Tenant.objects.filter(
            created_at__gte=month_start,
            created_at__lte=month_end
        ).count()
        data.append({
            'month': month_start.strftime('%b %Y'),
            'new_tenants': count
        })
    return data

def get_tenants_by_location():
    from rentals.models import RentalAgreement
    data = []
    for agreement in RentalAgreement.objects.filter(status='active').select_related('room__location', 'tenant'):
        data.append({
            'location': agreement.room.location.name,
            'tenant': agreement.tenant.name
        })
    location_counts = {}
    for item in data:
        location = item['location']
        if location not in location_counts:
            location_counts[location] = 0
        location_counts[location] += 1
    return [{'location': loc, 'count': count} for loc, count in location_counts.items()]

def get_recent_tenant_activity():
    from tenants.models import Tenant
    return Tenant.objects.order_by('-updated_at')[:5]

def get_location_metrics():
    from properties.models import Location
    return {
        'total': Location.objects.count(),
        'active': Location.objects.filter(is_active=True).count()
    }

def get_location_distribution():
    from properties.models import Location
    data = Location.objects.values('city').annotate(
        count=Count('id')
    ).order_by('city')
    return list(data)

def get_room_utilization():
    from properties.models import Room
    total_rooms = Room.objects.count()
    occupied_rooms = Room.objects.filter(status='occupied').count()
    return {
        'total_rooms': total_rooms,
        'occupied_rooms': occupied_rooms,
        'utilization_rate': round((occupied_rooms / total_rooms * 100), 1) if total_rooms > 0 else 0
    }

def get_property_performance():
    return {
        'average_rent': get_average_rent(),
        'maintenance_cost_per_room': get_maintenance_cost_per_room(),
        'occupancy_rate': get_occupancy_rate()
    }

def get_maintenance_by_location():
    from maintenance.models import MaintenanceRequest
    data = MaintenanceRequest.objects.select_related(
        'room__location'
    ).values('room__location__name').annotate(
        count=Count('id')
    ).order_by('-count')
    return list(data)

def get_average_rent():
    from rentals.models import RentalAgreement
    result = RentalAgreement.objects.filter(status='active').aggregate(
        avg_rent=Avg('rent_amount')
    )
    return float(result['avg_rent'] or 0)

def get_maintenance_cost_per_room():
    from maintenance.models import MaintenanceRequest
    from properties.models import Room
    total_cost = MaintenanceRequest.objects.filter(
        status='completed',
        actual_cost__isnull=False
    ).aggregate(total=Sum('actual_cost'))['total'] or 0
    total_rooms = Room.objects.count()
    if total_rooms == 0:
        return 0
    return round(float(total_cost) / total_rooms, 2)


def get_pending_tasks_for_user(user):
    """
    Get pending tasks that require action from the current user
    Returns tasks grouped by type for different staff roles
    """
    tasks = {
        'maintenance_requests': [],
        'payment_verifications': [],
        'escalated_issues': [],
        'total_count': 0
    }

    # Check user role
    user_role = None
    if hasattr(user, 'staff_profile') and user.staff_profile:
        user_role = user.staff_profile.role

    # Maintenance tasks based on role
    from maintenance.models import MaintenanceRequest

    if user_role == 'manager':
        # Managers see escalated and overdue maintenance
        escalated = MaintenanceRequest.objects.filter(
            Q(status='pending', priority='urgent') |
            Q(status='in_progress', priority='urgent')
        ).select_related('tenant', 'room__location').order_by('-requested_date')[:5]

        overdue = MaintenanceRequest.objects.filter(
            status__in=['pending', 'in_progress'],
            requested_date__lt=timezone.now() - timedelta(days=7)
        ).exclude(id__in=[m.id for m in escalated]).select_related(
            'tenant', 'room__location'
        ).order_by('-requested_date')[:5]

        tasks['escalated_issues'].extend([
            {
                'id': req.id,
                'type': 'escalated_maintenance',
                'title': f"Urgent: {req.title}",
                'description': f"{req.description[:50]}..." if len(req.description) > 50 else req.description,
                'priority': req.priority,
                'days_pending': req.days_pending,
                'tenant': req.tenant.name,
                'room': f"{req.room.room_number}",
                'location': req.room.location.name,
                'url': f"/maintenance/{req.id}/"
            } for req in escalated
        ])

        tasks['escalated_issues'].extend([
            {
                'id': req.id,
                'type': 'overdue_maintenance',
                'title': f"Overdue: {req.title}",
                'description': f"{req.description[:50]}..." if len(req.description) > 50 else req.description,
                'priority': req.priority,
                'days_pending': req.days_pending,
                'tenant': req.tenant.name,
                'room': f"{req.room.room_number}",
                'location': req.room.location.name,
                'url': f"/maintenance/{req.id}/"
            } for req in overdue
        ])

    elif user_role == 'caretaker':
        # Caretakers see pending assignments and completions
        pending_assignment = MaintenanceRequest.objects.filter(
            status='pending'
        ).select_related('tenant', 'room__location').order_by('-requested_date')[:5]

        needs_completion = MaintenanceRequest.objects.filter(
            status='in_progress',
            assigned_to__isnull=False
        ).select_related('tenant', 'room__location').order_by('-assigned_date')[:5]

        tasks['maintenance_requests'].extend([
            {
                'id': req.id,
                'type': 'assign_maintenance',
                'title': f"Assign: {req.title}",
                'description': f"{req.description[:50]}..." if len(req.description) > 50 else req.description,
                'priority': req.priority,
                'days_pending': req.days_pending,
                'tenant': req.tenant.name,
                'room': f"{req.room.room_number}",
                'location': req.room.location.name,
                'url': f"/maintenance/{req.id}/"
            } for req in pending_assignment
        ])

        tasks['maintenance_requests'].extend([
            {
                'id': req.id,
                'type': 'complete_maintenance',
                'title': f"Complete: {req.title}",
                'description': f"Assigned to {req.assigned_to}",
                'priority': req.priority,
                'days_pending': req.days_pending,
                'tenant': req.tenant.name,
                'room': f"{req.room.room_number}",
                'location': req.room.location.name,
                'url': f"/maintenance/{req.id}/"
            } for req in needs_completion
        ])

    elif user_role == 'cleaner':
        # Cleaners see maintenance assigned to them
        assigned_to_me = MaintenanceRequest.objects.filter(
            status='in_progress',
            assigned_to=user.get_full_name()
        ).select_related('tenant', 'room__location').order_by('-assigned_date')[:10]

        tasks['maintenance_requests'].extend([
            {
                'id': req.id,
                'type': 'my_maintenance',
                'title': f"My Task: {req.title}",
                'description': req.description[:50] + "..." if len(req.description) > 50 else req.description,
                'priority': req.priority,
                'days_pending': req.days_pending,
                'tenant': req.tenant.name,
                'room': f"{req.room.room_number}",
                'location': req.room.location.name,
                'url': f"/maintenance/{req.id}/"
            } for req in assigned_to_me
        ])

    # Payment verifications for caretakers and managers
    if user_role in ['caretaker', 'manager']:
        from payments.models import Payment

        pending_payments = Payment.objects.filter(
            status='pending'
        ).select_related('tenant', 'room', 'rental_agreement').order_by('-created_at')[:5]

        tasks['payment_verifications'].extend([
            {
                'id': payment.id,
                'type': 'verify_payment',
                'title': f"Verify Payment: KSh {payment.amount}",
                'description': f"{payment.payment_method.upper()} - {payment.reference_number}",
                'amount': payment.amount,
                'method': payment.payment_method,
                'tenant': payment.tenant.name if payment.tenant else 'Unknown',
                'url': f"/payments/{payment.id}/"
            } for payment in pending_payments
        ])

    # Calculate total count
    tasks['total_count'] = (
        len(tasks['maintenance_requests']) +
        len(tasks['payment_verifications']) +
        len(tasks['escalated_issues'])
    )

    return tasks


def manager_required(user):
    """Check if user is a manager or superuser"""
    if user.is_superuser:
        return True
    if hasattr(user, 'staff_profile') and user.staff_profile:
        return user.staff_profile.role == 'manager'
    return False


@login_required
@user_passes_test(manager_required)
def audit_log_view(request):
    """Audit log viewer for managers - read-only"""
    from workflows.services.audit import WorkflowAuditLog

    # Get filter parameters
    event_type = request.GET.get('event_type', '')
    user_filter = request.GET.get('user', '')
    instance_type = request.GET.get('instance_type', '')
    days = int(request.GET.get('days', 30))

    # Base queryset
    since_date = timezone.now() - timedelta(days=days)
    queryset = WorkflowAuditLog.objects.filter(timestamp__gte=since_date)

    # Apply filters
    if event_type:
        queryset = queryset.filter(event_type=event_type)
    if user_filter:
        queryset = queryset.filter(user__username__icontains=user_filter)
    if instance_type:
        queryset = queryset.filter(instance_type=instance_type)

    # Order by most recent first
    queryset = queryset.select_related('user').order_by('-timestamp')

    # Paginate results (50 per page)
    paginator = Paginator(queryset, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get filter options for dropdowns
    event_types = WorkflowAuditLog.objects.values_list('event_type', flat=True).distinct()
    instance_types = WorkflowAuditLog.objects.values_list('instance_type', flat=True).distinct()
    users = WorkflowAuditLog.objects.values_list('user__username', flat=True).distinct()

    context = {
        'page_title': 'Audit Log Review',
        'page_obj': page_obj,
        'event_types': sorted(event_types),
        'instance_types': sorted(instance_types),
        'users': sorted(users),
        'current_filters': {
            'event_type': event_type,
            'user': user_filter,
            'instance_type': instance_type,
            'days': days
        }
    }

    return render(request, 'dashboard/audit_log.html', context)


@login_required
def dashboard_metrics_api(request):
    """
    API endpoint for real-time dashboard metrics
    Returns JSON data for dashboard updates
    """
    from django.http import JsonResponse

    try:
        # Get current metrics
        metrics = {
            'total_tenants': get_tenant_metrics(),
            'total_rooms': get_room_metrics(),
            'total_payments': get_payment_metrics(),
            'total_maintenance': get_maintenance_metrics(),
            'occupancy_rate': get_occupancy_rate(),
            'monthly_revenue': get_monthly_revenue(),
            'pending_maintenance': get_pending_maintenance_count(),
            'collection_rate': get_collection_rate(),
            'avg_revenue_per_room': get_avg_revenue_per_room(),
            'dso': get_days_sales_outstanding(),
            'tenant_growth': get_tenant_growth_rate(),
            'revenue_change': get_revenue_change_percentage(),
        }

        # Add timestamp for cache busting
        metrics['timestamp'] = timezone.now().isoformat()

        return JsonResponse({
            'success': True,
            'data': metrics
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# Additional metric calculation functions for real-time updates

def get_collection_rate():
    """Calculate payment collection rate for current month"""
    try:
        from django.db.models import Sum, Count
        from payments.models import Payment
        from rentals.models import RentalAgreement

        now = timezone.now()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Expected payments (active agreements)
        expected_payments = RentalAgreement.objects.filter(
            status='active',
            start_date__lte=now.date()
        ).count()

        if expected_payments == 0:
            return 0

        # Actual collected payments this month
        collected_payments = Payment.objects.filter(
            status='completed',
            payment_date__gte=start_of_month
        ).count()

        return round((collected_payments / expected_payments) * 100, 1)

    except Exception:
        return 0


def get_avg_revenue_per_room():
    """Calculate average revenue per occupied room"""
    try:
        from properties.models import Room
        from rentals.models import RentalAgreement

        # Get occupied rooms
        occupied_rooms = Room.objects.filter(status='occupied').count()
        if occupied_rooms == 0:
            return 0

        # Get total monthly revenue
        total_revenue = get_monthly_revenue()
        return total_revenue / occupied_rooms

    except Exception:
        return 0


def get_days_sales_outstanding():
    """Calculate Days Sales Outstanding (DSO)"""
    try:
        from payments.models import Payment

        # Get average payment time for completed payments in last 90 days
        ninety_days_ago = timezone.now() - timedelta(days=90)

        payments = Payment.objects.filter(
            status='completed',
            payment_date__gte=ninety_days_ago
        ).exclude(
            created_at__isnull=True
        )

        if not payments.exists():
            return 0

        # Calculate average days between creation and payment
        total_days = 0
        count = 0

        for payment in payments:
            if payment.created_at and payment.payment_date:
                days = (payment.payment_date.date() - payment.created_at.date()).days
                if days >= 0:  # Only count valid positive delays
                    total_days += days
                    count += 1

        return round(total_days / count, 1) if count > 0 else 0

    except Exception:
        return 0


def get_tenant_growth_rate():
    """Calculate tenant growth rate (last 30 days vs previous 30 days)"""
    try:
        from tenants.models import Tenant

        now = timezone.now()
        thirty_days_ago = now - timedelta(days=30)
        sixty_days_ago = now - timedelta(days=60)

        # Tenants in last 30 days
        recent_tenants = Tenant.objects.filter(
            created_at__gte=thirty_days_ago
        ).count()

        # Tenants in previous 30 days
        previous_tenants = Tenant.objects.filter(
            created_at__gte=sixty_days_ago,
            created_at__lt=thirty_days_ago
        ).count()

        if previous_tenants == 0:
            return recent_tenants * 100  # Growth from 0

        growth_rate = ((recent_tenants - previous_tenants) / previous_tenants) * 100
        return round(growth_rate, 1)

    except Exception:
        return 0


def get_revenue_change_percentage():
    """Calculate revenue change from previous month"""
    try:
        from payments.models import Payment

        now = timezone.now()
        current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        previous_month_start = (current_month_start - timedelta(days=1)).replace(day=1)

        # Current month revenue
        current_revenue = Payment.objects.filter(
            status='completed',
            payment_date__gte=current_month_start
        ).aggregate(total=Sum('amount'))['total'] or 0

        # Previous month revenue
        previous_revenue = Payment.objects.filter(
            status='completed',
            payment_date__gte=previous_month_start,
            payment_date__lt=current_month_start
        ).aggregate(total=Sum('amount'))['total'] or 0

        if previous_revenue == 0:
            return current_revenue * 100 if current_revenue > 0 else 0

        change_percentage = ((current_revenue - previous_revenue) / previous_revenue) * 100
        return round(change_percentage, 1)

    except Exception:
        return 0
