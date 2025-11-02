"""
Basic reports utils - simple implementations
"""

from django.db.models import Sum, Count
from django.utils import timezone
from decimal import Decimal


def generate_financial_report(filters=None):
    """Generate basic financial report"""
    from payments.models import Payment

    if not filters:
        filters = {}

    # Simple date filtering
    start_date = filters.get('start_date')
    end_date = filters.get('end_date')

    payments = Payment.objects.all()
    if start_date and end_date:
        payments = payments.filter(payment_date__range=(start_date, end_date))

    # Basic financial metrics
    total_revenue = payments.filter(status='completed').aggregate(
        total=Sum('amount')
    )['total'] or 0

    pending_amount = payments.filter(status='pending').aggregate(
        total=Sum('amount')
    )['total'] or 0

    return {
        'total_revenue': float(total_revenue),
        'pending_amount': float(pending_amount),
        'total_payments': payments.count(),
        'completed_payments': payments.filter(status='completed').count(),
    }


def generate_tenant_report(filters=None):
    """Generate basic tenant report"""
    from tenants.models import Tenant

    if not filters:
        filters = {}

    # Basic tenant statistics
    total_tenants = Tenant.objects.count()
    active_tenants = Tenant.objects.filter(tenant_status='active').count()
    prospective_tenants = Tenant.objects.filter(tenant_status='prospective').count()

    return {
        'total_tenants': total_tenants,
        'active_tenants': active_tenants,
        'prospective_tenants': prospective_tenants,
    }


def generate_occupancy_report(filters=None):
    """Generate basic occupancy report"""
    from properties.models import Room

    # Basic room statistics
    total_rooms = Room.objects.count()
    occupied_rooms = Room.objects.filter(status='occupied').count()
    vacant_rooms = Room.objects.filter(status='vacant').count()

    occupancy_rate = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0

    return {
        'total_rooms': total_rooms,
        'occupied_rooms': occupied_rooms,
        'vacant_rooms': vacant_rooms,
        'occupancy_rate': round(occupancy_rate, 2),
    }


def generate_revenue_report(filters=None):
    """Generate basic revenue report"""
    return generate_financial_report(filters)  # Reuse financial logic


def generate_maintenance_report(filters=None):
    """Generate basic maintenance report"""
    from maintenance.models import MaintenanceRequest

    if not filters:
        filters = {}

    # Basic maintenance statistics
    total_requests = MaintenanceRequest.objects.count()
    pending_requests = MaintenanceRequest.objects.filter(status='pending').count()
    completed_requests = MaintenanceRequest.objects.filter(status='completed').count()

    return {
        'total_requests': total_requests,
        'pending_requests': pending_requests,
        'completed_requests': completed_requests,
    }


def generate_collection_report(filters=None):
    """Generate basic collection report"""
    from payments.models import Payment

    # Payment collection status
    pending_payments = Payment.objects.filter(status='pending').aggregate(
        total=Sum('amount')
    )['total'] or 0

    overdue_payments = Payment.objects.filter(
        status='pending',
        payment_date__lt=timezone.now().date()
    ).aggregate(total=Sum('amount'))['total'] or 0

    return {
        'pending_amount': float(pending_payments),
        'overdue_amount': float(overdue_payments),
    }


def generate_property_report(filters=None):
    """Generate basic property report"""
    from properties.models import Location, Room

    # Property statistics (using Location as Property equivalent)
    total_locations = Location.objects.count()
    total_rooms = Room.objects.count()

    # Room breakdown by status
    occupied_rooms = Room.objects.filter(status='occupied').count()
    vacant_rooms = Room.objects.filter(status='available').count()
    maintenance_rooms = Room.objects.filter(status='maintenance').count()

    return {
        'total_locations': total_locations,
        'total_rooms': total_rooms,
        'occupied_rooms': occupied_rooms,
        'vacant_rooms': vacant_rooms,
        'maintenance_rooms': maintenance_rooms,
        'occupancy_rate': round((occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0, 2)
    }


def export_report_json(report_data, report_type):
    """Export report as JSON"""
    return {
        'report_type': report_type,
        'generated_at': timezone.now().isoformat(),
        'data': report_data
    }


def export_report_csv(report_data, report_type):
    """Export report as CSV (basic implementation)"""
    from django.http import HttpResponse
    import csv

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{report_type}_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Key', 'Value'])

    for key, value in report_data.items():
        writer.writerow([key, value])

    return response


def export_report_pdf(report_data, report_type):
    """Basic PDF export - return JSON as PDF file"""
    from django.http import HttpResponse
    import json
    response_data = export_report_json(report_data, report_type)
    response = HttpResponse(json.dumps(response_data, indent=2))
    response['Content-Type'] = 'application/pdf'
    response['Content-Disposition'] = f'attachment; filename="{report_type}_report.pdf"'
    return response


def export_report_excel(report_data, report_type):
    """Basic Excel export - return JSON as Excel file"""
    from django.http import HttpResponse
    import json
    response_data = export_report_json(report_data, report_type)
    response = HttpResponse(json.dumps(response_data, indent=2))
    response['Content-Type'] = 'application/vnd.ms-excel'
    response['Content-Disposition'] = f'attachment; filename="{report_type}_report.xlsx"'
    return response
