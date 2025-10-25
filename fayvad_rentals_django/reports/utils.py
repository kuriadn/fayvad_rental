"""
Report generation utilities
Functions for generating various business reports
"""

from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta
import json
from django.http import HttpResponse
from .models import ReportType

def generate_occupancy_report(filters=None):
    """Generate occupancy report data"""
    from properties.models import Room, Location
    from rentals.models import RentalAgreement

    if filters is None:
        filters = {}

    # Base querysets
    rooms = Room.objects.select_related('location')
    agreements = RentalAgreement.objects.select_related('tenant', 'room')

    # Apply filters
    start_date = filters.get('start_date')
    end_date = filters.get('end_date')
    location_id = filters.get('location')
    room_type = filters.get('room_type')

    if location_id:
        rooms = rooms.filter(location_id=location_id)
        agreements = agreements.filter(room__location_id=location_id)

    if room_type:
        rooms = rooms.filter(room_type=room_type)
        agreements = agreements.filter(room__room_type=room_type)

    # Calculate metrics
    total_rooms = rooms.count()
    occupied_rooms = agreements.filter(status='active').count()
    occupancy_rate = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0

    # Room breakdown by type
    room_breakdown = rooms.values('room_type').annotate(
        total=Count('id'),
        occupied=Count('id', filter=Q(rental_agreement__status='active'))
    ).order_by('room_type')

    # Location breakdown
    location_breakdown = []
    for location in Location.objects.all():
        if location_id and str(location.id) != location_id:
            continue

        loc_rooms = rooms.filter(location=location)
        loc_agreements = agreements.filter(room__location=location, status='active')
        loc_occupancy = (loc_agreements.count() / loc_rooms.count() * 100) if loc_rooms.count() > 0 else 0

        location_breakdown.append({
            'location': location.name,
            'total_rooms': loc_rooms.count(),
            'occupied_rooms': loc_agreements.count(),
            'occupancy_rate': round(loc_occupancy, 1)
        })

    # Insights
    insights = []
    if occupancy_rate > 90:
        insights.append("Excellent occupancy rate - consider expansion opportunities")
    elif occupancy_rate < 70:
        insights.append("Low occupancy rate - review marketing and pricing strategies")
    else:
        insights.append("Occupancy rate is within acceptable range")

    # Room type utilization
    for room_type_data in room_breakdown:
        rate = (room_type_data['occupied'] / room_type_data['total'] * 100) if room_type_data['total'] > 0 else 0
        if rate < 60:
            insights.append(f"Low utilization for {room_type_data['room_type']} rooms ({rate:.1f}%)")

    return {
        'report_type': 'occupancy',
        'generated_at': timezone.now().isoformat(),
        'period': f"{start_date or 'All time'} to {end_date or 'Present'}",
        'filters': filters,
        'summary': {
            'total_rooms': total_rooms,
            'occupied_rooms': occupied_rooms,
            'vacant_rooms': total_rooms - occupied_rooms,
            'occupancy_rate': round(occupancy_rate, 1)
        },
        'details': {
            'room_breakdown': list(room_breakdown),
            'location_breakdown': location_breakdown
        },
        'insights': insights
    }

def generate_revenue_report(filters=None):
    """Generate revenue report data"""
    from payments.models import Payment
    from tenants.models import Tenant
    from properties.models import Room

    if filters is None:
        filters = {}

    # Base queryset
    payments = Payment.objects.filter(status='completed').select_related('tenant', 'room')

    # Apply filters
    start_date = filters.get('start_date')
    end_date = filters.get('end_date')
    tenant_id = filters.get('tenant')
    location_id = filters.get('location')
    payment_method = filters.get('payment_method')

    if start_date:
        payments = payments.filter(payment_date__gte=start_date)
    if end_date:
        payments = payments.filter(payment_date__lte=end_date)
    if tenant_id:
        payments = payments.filter(tenant_id=tenant_id)
    if location_id:
        payments = payments.filter(room__location_id=location_id)
    if payment_method:
        payments = payments.filter(payment_method=payment_method)

    # Calculate metrics
    total_revenue = payments.aggregate(total=Sum('amount'))['total'] or 0
    payment_count = payments.count()
    avg_payment = total_revenue / payment_count if payment_count > 0 else 0

    # Revenue by tenant
    tenant_revenue = payments.values('tenant__name').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')[:10]

    # Revenue by payment method
    method_revenue = payments.values('payment_method').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')

    # Monthly revenue trend
    monthly_revenue = payments.extra(
        select={'month': "DATE_TRUNC('month', payment_date)"}
    ).values('month').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('month')

    # Insights
    insights = []
    if total_revenue > 0:
        insights.append(f"Total revenue: KSh {total_revenue:,.0f}")
    if payment_count > 0:
        insights.append(f"Average payment: KSh {avg_payment:,.0f}")

    # Check payment method distribution
    if method_revenue:
        top_method = method_revenue[0]
        method_percentage = (top_method['total'] / total_revenue * 100) if total_revenue > 0 else 0
        if method_percentage > 80:
            insights.append(f"Heavily reliant on {top_method['payment_method']} payments ({method_percentage:.1f}%)")

    return {
        'report_type': 'revenue',
        'generated_at': timezone.now().isoformat(),
        'period': f"{start_date or 'All time'} to {end_date or 'Present'}",
        'filters': filters,
        'summary': {
            'total_revenue': float(total_revenue),
            'payment_count': payment_count,
            'average_payment': round(float(avg_payment), 2)
        },
        'details': {
            'tenant_revenue_breakdown': list(tenant_revenue),
            'payment_method_breakdown': list(method_revenue),
            'monthly_revenue': list(monthly_revenue)
        },
        'insights': insights
    }

def generate_maintenance_report(filters=None):
    """Generate maintenance report data"""
    from maintenance.models import MaintenanceRequest

    if filters is None:
        filters = {}

    # Base queryset
    requests = MaintenanceRequest.objects.select_related('tenant', 'room__location')

    # Apply filters
    start_date = filters.get('start_date')
    end_date = filters.get('end_date')
    priority = filters.get('priority')
    status = filters.get('status')
    location_id = filters.get('location')

    if start_date:
        requests = requests.filter(requested_date__gte=start_date)
    if end_date:
        requests = requests.filter(requested_date__lte=end_date)
    if priority:
        requests = requests.filter(priority=priority)
    if status:
        requests = requests.filter(status=status)
    if location_id:
        requests = requests.filter(room__location_id=location_id)

    # Calculate metrics
    total_requests = requests.count()
    pending_requests = requests.filter(status='pending').count()
    in_progress_requests = requests.filter(status='in_progress').count()
    completed_requests = requests.filter(status='completed').count()

    # Average resolution time
    completed_reqs = requests.filter(status='completed', completed_date__isnull=False)
    avg_resolution_days = 0
    if completed_reqs.exists():
        total_days = sum(
            (req.completed_date - req.requested_date).days
            for req in completed_reqs
        )
        avg_resolution_days = round(total_days / completed_reqs.count(), 1)

    # Requests by status
    status_breakdown = requests.values('status').annotate(
        count=Count('id')
    ).order_by('status')

    # Requests by priority
    priority_breakdown = requests.values('priority').annotate(
        count=Count('id')
    ).order_by('priority')

    # Cost analysis
    total_cost = requests.filter(
        status='completed',
        actual_cost__isnull=False
    ).aggregate(total=Sum('actual_cost'))['total'] or 0

    # Overdue requests
    overdue_requests = [req for req in requests.filter(
        status__in=['pending', 'in_progress']
    ) if req.is_overdue]
    overdue_count = len(overdue_requests)

    # Insights
    insights = []
    if overdue_count > 0:
        insights.append(f"{overdue_count} requests are overdue - review maintenance priorities")
    if avg_resolution_days > 7:
        insights.append(f"Average resolution time ({avg_resolution_days} days) exceeds target")
    if total_cost > 0:
        insights.append(f"Total maintenance cost: KSh {total_cost:,.0f}")

    return {
        'report_type': 'maintenance',
        'generated_at': timezone.now().isoformat(),
        'period': f"{start_date or 'All time'} to {end_date or 'Present'}",
        'filters': filters,
        'summary': {
            'total_requests': total_requests,
            'pending_requests': pending_requests,
            'in_progress_requests': in_progress_requests,
            'completed_requests': completed_requests,
            'overdue_requests': overdue_count,
            'average_resolution_days': avg_resolution_days,
            'total_cost': float(total_cost)
        },
        'details': {
            'requests_by_status': list(status_breakdown),
            'requests_by_priority': list(priority_breakdown),
            'cost_analysis': {
                'total_cost': float(total_cost),
                'average_cost_per_request': round(float(total_cost) / completed_requests, 2) if completed_requests > 0 else 0
            }
        },
        'insights': insights
    }

def generate_collection_report(filters=None):
    """Generate collection report data"""
    from payments.models import Payment
    from rentals.models import RentalAgreement
    from tenants.models import Tenant

    if filters is None:
        filters = {}

    # Base querysets
    payments = Payment.objects.filter(status='completed').select_related('tenant')
    agreements = RentalAgreement.objects.filter(status='active').select_related('tenant')

    # Apply filters
    start_date = filters.get('start_date')
    end_date = filters.get('end_date')
    status = filters.get('status')
    location_id = filters.get('location')

    if start_date:
        payments = payments.filter(payment_date__gte=start_date)
    if end_date:
        payments = payments.filter(payment_date__lte=end_date)
    if location_id:
        payments = payments.filter(room__location_id=location_id)
        agreements = agreements.filter(room__location_id=location_id)

    # Calculate collection metrics
    total_expected = agreements.aggregate(
        total=Sum('rent_amount')
    )['total'] or 0

    total_collected = payments.aggregate(
        total=Sum('amount')
    )['total'] or 0

    collection_rate = (total_collected / total_expected * 100) if total_expected > 0 else 0

    # Overdue accounts
    overdue_accounts = []
    for agreement in agreements:
        outstanding = agreement.outstanding_balance
        if outstanding > 0:
            overdue_accounts.append({
                'tenant': agreement.tenant.name,
                'amount_due': outstanding,
                'days_overdue': 0  # Would need payment due date logic
            })

    # Payment status breakdown
    payment_status = payments.values('status').annotate(
        count=Count('id'),
        total=Sum('amount')
    ).order_by('status')

    # Insights
    insights = []
    if collection_rate < 80:
        insights.append(f"Collection rate ({collection_rate:.1f}%) is below target - review collection processes")
    if len(overdue_accounts) > 0:
        insights.append(f"{len(overdue_accounts)} accounts have outstanding balances")

    return {
        'report_type': 'collection',
        'generated_at': timezone.now().isoformat(),
        'period': f"{start_date or 'All time'} to {end_date or 'Present'}",
        'filters': filters,
        'summary': {
            'total_expected': float(total_expected),
            'total_collected': float(total_collected),
            'collection_rate': round(collection_rate, 1),
            'outstanding_amount': float(total_expected - total_collected)
        },
        'details': {
            'payment_status_breakdown': list(payment_status),
            'overdue_accounts': overdue_accounts[:10]  # Top 10 overdue accounts
        },
        'insights': insights
    }

def generate_tenant_report(filters=None):
    """Generate tenant report data"""
    from tenants.models import Tenant
    from rentals.models import RentalAgreement
    from payments.models import Payment

    if filters is None:
        filters = {}

    # Base querysets
    tenants = Tenant.objects.all()
    agreements = RentalAgreement.objects.select_related('tenant', 'room__location')

    # Apply filters
    status = filters.get('status')
    location_id = filters.get('location')
    start_date = filters.get('start_date')
    end_date = filters.get('end_date')

    if status:
        tenants = tenants.filter(tenant_status=status)
    if location_id:
        agreements = agreements.filter(room__location_id=location_id)
        tenant_ids = agreements.values_list('tenant_id', flat=True)
        tenants = tenants.filter(id__in=tenant_ids)

    # Calculate tenant metrics
    total_tenants = tenants.count()
    active_tenants = tenants.filter(tenant_status='active').count()
    prospective_tenants = tenants.filter(tenant_status='prospective').count()

    # Tenant status distribution
    status_distribution = tenants.values('tenant_status').annotate(
        count=Count('id')
    ).order_by('tenant_status')

    # Payment history summary
    tenant_payments = Payment.objects.filter(
        status='completed',
        tenant__in=tenants
    ).values('tenant__name').annotate(
        total_paid=Sum('amount'),
        payment_count=Count('id')
    ).order_by('-total_paid')[:10]

    # Insights
    insights = []
    if active_tenants > 0:
        insights.append(f"{active_tenants} active tenants generating revenue")
    if prospective_tenants > 0:
        insights.append(f"{prospective_tenants} prospective tenants in pipeline")

    return {
        'report_type': 'tenant',
        'generated_at': timezone.now().isoformat(),
        'period': f"{start_date or 'All time'} to {end_date or 'Present'}",
        'filters': filters,
        'summary': {
            'total_tenants': total_tenants,
            'active_tenants': active_tenants,
            'prospective_tenants': prospective_tenants,
            'inactive_tenants': total_tenants - active_tenants - prospective_tenants
        },
        'details': {
            'tenant_status_distribution': list(status_distribution),
            'top_paying_tenants': list(tenant_payments)
        },
        'insights': insights
    }

def generate_financial_report(filters=None):
    """Generate comprehensive financial report"""
    if filters is None:
        filters = {}

    # Get data from other reports
    revenue_data = generate_revenue_report(filters)
    collection_data = generate_collection_report(filters)

    # Combine financial insights
    total_revenue = revenue_data['summary']['total_revenue']
    collection_rate = collection_data['summary']['collection_rate']
    outstanding_amount = collection_data['summary']['outstanding_amount']

    insights = revenue_data['insights'] + collection_data['insights']
    insights.append(f"Collection efficiency: {collection_rate:.1f}%")
    insights.append(f"Outstanding receivables: KSh {outstanding_amount:,.0f}")

    return {
        'report_type': 'financial',
        'generated_at': timezone.now().isoformat(),
        'period': revenue_data['period'],
        'filters': filters,
        'summary': {
            'total_revenue': total_revenue,
            'collection_rate': collection_rate,
            'outstanding_receivables': outstanding_amount,
            'net_collections': total_revenue * (collection_rate / 100)
        },
        'details': {
            'revenue_breakdown': revenue_data['details'],
            'collection_analysis': collection_data['details']
        },
        'insights': insights
    }

# Export functions

def export_report_json(report_data, report_type):
    """Export report as JSON"""
    return {
        'success': True,
        'report_type': report_type,
        'data': report_data,
        'exported_at': timezone.now().isoformat(),
        'format': 'json'
    }

def export_report_csv(report_data, report_type):
    """Export report as CSV"""
    response = HttpResponse(content_type='text/csv')
    timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
    response['Content-Disposition'] = f'attachment; filename="{report_type}_report_{timestamp}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Report Type', 'Generated At', 'Period'])
    writer.writerow([
        report_data.get('report_type', report_type),
        report_data.get('generated_at', timezone.now().isoformat()),
        report_data.get('period', 'N/A')
    ])

    # Write summary data
    writer.writerow([])
    writer.writerow(['Summary'])
    summary = report_data.get('summary', {})
    for key, value in summary.items():
        writer.writerow([key.replace('_', ' ').title(), value])

    # Write insights
    writer.writerow([])
    writer.writerow(['Insights'])
    insights = report_data.get('insights', [])
    for insight in insights:
        writer.writerow([insight])

    return response

def export_report_pdf(report_data, report_type):
    """Export report as PDF (simplified text version)"""
    # In a real implementation, you would use a PDF library like reportlab
    response = HttpResponse(content_type='application/pdf')
    timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
    response['Content-Disposition'] = f'attachment; filename="{report_type}_report_{timestamp}.pdf"'

    # Simple text-based PDF simulation
    content = f"""
    {report_type.title()} Report
    Generated: {report_data.get('generated_at', timezone.now().isoformat())}
    Period: {report_data.get('period', 'N/A')}

    Summary:
    {json.dumps(report_data.get('summary', {}), indent=2, default=str)}

    Insights:
    {chr(10).join(report_data.get('insights', []))}
    """

    response.write(content.encode('utf-8'))
    return response

def export_report_excel(report_data, report_type):
    """Export report as Excel (simplified text version)"""
    # In a real implementation, you would use openpyxl or similar
    response = HttpResponse(content_type='application/vnd.ms-excel')
    timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
    response['Content-Disposition'] = f'attachment; filename="{report_type}_report_{timestamp}.xls"'

    # Simple tab-separated format
    summary_lines = chr(10).join([f"{k}\t{v}" for k, v in report_data.get('summary', {}).items()])
    insights_lines = chr(10).join(report_data.get('insights', []))
    content = f"""Report Type\t{report_data.get('report_type', report_type)}
Generated At\t{report_data.get('generated_at', timezone.now().isoformat())}
Period\t{report_data.get('period', 'N/A')}

Summary
{summary_lines}

Insights
{insights_lines}
"""

    response.write(content.encode('utf-8'))
    return response
