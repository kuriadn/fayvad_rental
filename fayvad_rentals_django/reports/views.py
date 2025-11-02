"""
Report generation views
Financial, occupancy, maintenance, and other business reports
"""

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum, Avg, Q
from django.http import HttpResponse, JsonResponse, Http404
from django.utils import timezone
from datetime import datetime, timedelta
import json
import csv
from .models import ReportType, ExportFormat, GeneratedReport
from .utils import (
    generate_occupancy_report, generate_revenue_report, generate_maintenance_report,
    generate_collection_report, generate_tenant_report, generate_financial_report, generate_property_report,
    export_report_json, export_report_csv, export_report_pdf, export_report_excel
)

@login_required
def report_list(request):
    """List all available reports"""
    # Define available reports based on the original FastAPI implementation
    reports = [
        {
            "id": "financial",
            "name": "Financial Report",
            "description": "Comprehensive financial overview including revenue, expenses, and profitability",
            "category": "Finance",
            "formats": ["json", "csv", "pdf", "excel"],
            "filters": ["date_range", "location", "payment_method"]
        },
        {
            "id": "occupancy",
            "name": "Occupancy Report",
            "description": "Property occupancy rates, room utilization, and availability analysis",
            "category": "Operations",
            "formats": ["json", "csv", "pdf", "excel"],
            "filters": ["date_range", "location", "room_type"]
        },
        {
            "id": "maintenance",
            "name": "Maintenance Report",
            "description": "Maintenance requests, resolution times, and cost analysis",
            "category": "Operations",
            "formats": ["json", "csv", "pdf", "excel"],
            "filters": ["date_range", "priority", "status", "location"]
        },
        {
            "id": "tenant",
            "name": "Tenant Report",
            "description": "Tenant information, payment history, and occupancy details",
            "category": "Tenants",
            "formats": ["json", "csv", "pdf", "excel"],
            "filters": ["status", "location", "date_range"]
        },
        {
            "id": "revenue",
            "name": "Revenue Report",
            "description": "Detailed revenue analysis by tenant, property, and time period",
            "category": "Finance",
            "formats": ["json", "csv", "pdf", "excel"],
            "filters": ["date_range", "tenant", "location", "payment_method"]
        },
        {
            "id": "collection",
            "name": "Collection Report",
            "description": "Payment collection status, overdue accounts, and collection efficiency",
            "category": "Finance",
            "formats": ["json", "csv", "pdf", "excel"],
            "filters": ["date_range", "status", "location"]
        },
        {
            "id": "property",
            "name": "Property Report",
            "description": "Property and location information, room details, and occupancy statistics",
            "category": "Operations",
            "formats": ["json", "csv", "pdf", "excel"],
            "filters": ["location", "room_type"]
        }
    ]

    context = {
        'page_title': 'Reports',
        'reports': reports,
        'total_reports': len(reports),
    }
    return render(request, 'reports/report_list.html', context)

@login_required
def report_generate(request, report_type):
    """Generate a specific report"""
    if request.method == 'POST':
        # Get form data
        filters = {}
        format_type = request.POST.get('format', 'json')

        # Extract filters based on report type
        if report_type == 'financial':
            filters = extract_financial_filters(request.POST)
        elif report_type == 'occupancy':
            filters = extract_occupancy_filters(request.POST)
        elif report_type == 'maintenance':
            filters = extract_maintenance_filters(request.POST)
        elif report_type == 'tenant':
            filters = extract_tenant_filters(request.POST)
        elif report_type == 'revenue':
            filters = extract_revenue_filters(request.POST)
        elif report_type == 'collection':
            filters = extract_collection_filters(request.POST)
        elif report_type == 'property':
            filters = extract_property_filters(request.POST)
        else:
            messages.error(request, f'Unknown report type: {report_type}')
            return redirect('reports:report_list')

        try:
            # Generate report data
            report_data = generate_report_data(report_type, filters)

            # Export in requested format
            if format_type == 'json':
                response_data = export_report_json(report_data, report_type)
                response = HttpResponse(
                    json.dumps(response_data, indent=2),
                    content_type='application/json'
                )
                response['Content-Disposition'] = f'attachment; filename="{report_type}_report.json"'
                return response
            elif format_type == 'csv':
                response = export_report_csv(report_data, report_type)
                return response
            elif format_type == 'pdf':
                response = export_report_pdf(report_data, report_type)
                print(f"DEBUG: PDF response content_type = {response.get('Content-Type')}")
                return response
            elif format_type == 'excel':
                response = export_report_excel(report_data, report_type)
                return response
            else:
                messages.error(request, f'Unsupported export format: {format_type}')
                return redirect('reports:report_list')

        except Exception as e:
            messages.error(request, f'Error generating report: {str(e)}')
            return redirect('reports:report_list')

    # GET request - show report generation form
    context = {
        'page_title': f'Generate {report_type.title()} Report',
        'report_type': report_type,
        'export_formats': ['json', 'csv', 'pdf', 'excel'],
    }
    return render(request, 'reports/report_generate.html', context)

@login_required
def report_download(request, report_id):
    """Download a previously generated report"""
    report = get_object_or_404(
        GeneratedReport.objects.select_related('generated_by'),
        id=report_id,
        generated_by=request.user
    )

    if not report.is_complete:
        messages.error(request, 'Report is still being generated')
        return redirect('reports:report_list')

    if report.is_expired:
        messages.error(request, 'Report has expired')
        return redirect('reports:report_list')

    if report.export_format == 'json':
        return JsonResponse(report.report_data)
    elif report.file:
        # For file-based reports
        try:
            response = HttpResponse(report.file.read(), content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{report.title}.{report.export_format}"'
            return response
        except:
            raise Http404("File not found")
    else:
        raise Http404("Report file not available")


@login_required
def api_generate_report(request):
    """API endpoint for report generation - returns JSON"""
    from django.http import JsonResponse

    # Security check: Prevent tenant users from accessing staff reports
    if hasattr(request.user, 'tenant_profile') and request.user.tenant_profile:
        return JsonResponse({'success': False, 'error': 'Access denied'}, status=403)

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

    # Get parameters
    report_type = request.POST.get('report_type')
    date_from = request.POST.get('date_from')
    date_to = request.POST.get('date_to')

    if not report_type:
        return JsonResponse({'success': False, 'error': 'report_type is required'})

    # Validate report type
    valid_types = ['financial', 'tenant', 'property', 'occupancy', 'maintenance', 'revenue', 'collection']
    if report_type not in valid_types:
        return JsonResponse({'success': False, 'error': f'Invalid report type: {report_type}'})

    try:
        # Prepare filters
        filters = {}
        if date_from:
            filters['start_date'] = date_from
        if date_to:
            filters['end_date'] = date_to

        # Generate report
        report_data = generate_report_data(report_type, filters)

        return JsonResponse({
            'success': True,
            'message': f'{report_type.title()} report generated successfully',
            'data': {
                'report_type': report_type,
                'date_range': {'from': date_from, 'to': date_to} if date_from or date_to else None,
                'generated_at': timezone.now().isoformat(),
                'results': report_data
            }
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error generating report: {str(e)}'
        }, status=500)


# Helper functions for filter extraction

def extract_financial_filters(post_data):
    """Extract financial report filters"""
    filters = {}
    if post_data.get('start_date'):
        filters['start_date'] = post_data['start_date']
    if post_data.get('end_date'):
        filters['end_date'] = post_data['end_date']
    if post_data.get('location'):
        filters['location'] = post_data['location']
    if post_data.get('payment_method'):
        filters['payment_method'] = post_data['payment_method']
    return filters

def extract_occupancy_filters(post_data):
    """Extract occupancy report filters"""
    filters = {}
    if post_data.get('start_date'):
        filters['start_date'] = post_data['start_date']
    if post_data.get('end_date'):
        filters['end_date'] = post_data['end_date']
    if post_data.get('location'):
        filters['location'] = post_data['location']
    if post_data.get('room_type'):
        filters['room_type'] = post_data['room_type']
    return filters

def extract_maintenance_filters(post_data):
    """Extract maintenance report filters"""
    filters = {}
    if post_data.get('start_date'):
        filters['start_date'] = post_data['start_date']
    if post_data.get('end_date'):
        filters['end_date'] = post_data['end_date']
    if post_data.get('priority'):
        filters['priority'] = post_data['priority']
    if post_data.get('status'):
        filters['status'] = post_data['status']
    if post_data.get('location'):
        filters['location'] = post_data['location']
    return filters

def extract_tenant_filters(post_data):
    """Extract tenant report filters"""
    filters = {}
    if post_data.get('status'):
        filters['status'] = post_data['status']
    if post_data.get('location'):
        filters['location'] = post_data['location']
    if post_data.get('start_date'):
        filters['start_date'] = post_data['start_date']
    if post_data.get('end_date'):
        filters['end_date'] = post_data['end_date']
    return filters

def extract_revenue_filters(post_data):
    """Extract revenue report filters"""
    filters = {}
    if post_data.get('start_date'):
        filters['start_date'] = post_data['start_date']
    if post_data.get('end_date'):
        filters['end_date'] = post_data['end_date']
    if post_data.get('tenant'):
        filters['tenant'] = post_data['tenant']
    if post_data.get('location'):
        filters['location'] = post_data['location']
    if post_data.get('payment_method'):
        filters['payment_method'] = post_data['payment_method']
    return filters

def extract_collection_filters(post_data):
    """Extract collection report filters"""
    filters = {}
    if post_data.get('start_date'):
        filters['start_date'] = post_data['start_date']
    if post_data.get('end_date'):
        filters['end_date'] = post_data['end_date']
    if post_data.get('status'):
        filters['status'] = post_data['status']
    if post_data.get('location'):
        filters['location'] = post_data['location']
    return filters

def extract_property_filters(post_data):
    """Extract property report filters"""
    filters = {}
    if post_data.get('location'):
        filters['location'] = post_data['location']
    if post_data.get('room_type'):
        filters['room_type'] = post_data['room_type']
    return filters


# Main report generation function

def generate_report_data(report_type, filters=None):
    """Generate report data based on type"""
    if filters is None:
        filters = {}

    if report_type == 'occupancy':
        return generate_occupancy_report(filters)
    elif report_type == 'revenue':
        return generate_revenue_report(filters)
    elif report_type == 'maintenance':
        return generate_maintenance_report(filters)
    elif report_type == 'collection':
        return generate_collection_report(filters)
    elif report_type == 'tenant':
        return generate_tenant_report(filters)
    elif report_type == 'financial':
        return generate_financial_report(filters)
    elif report_type == 'property':
        return generate_property_report(filters)
    else:
        raise ValueError(f"Unknown report type: {report_type}")
