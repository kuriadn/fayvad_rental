from django.contrib import admin
from .models import MaintenanceRequest

@admin.register(MaintenanceRequest)
class MaintenanceRequestAdmin(admin.ModelAdmin):
    """Admin for MaintenanceRequest model"""
    list_display = [
        'request_number', 'title', 'tenant_name', 'room_identifier',
        'priority', 'status', 'requested_date', 'is_overdue'
    ]
    list_filter = ['status', 'priority', 'requested_date', 'scheduled_date', 'completed_date']
    search_fields = [
        'request_number', 'title', 'description',
        'tenant__name', 'tenant__email',
        'room__room_number', 'room__location__name'
    ]
    readonly_fields = ['request_number', 'created_at', 'updated_at', 'requested_date']
    ordering = ['-requested_date']

    fieldsets = (
        ('Request Information', {
            'fields': ('request_number', 'title', 'description')
        }),
        ('Related Entities', {
            'fields': ('tenant', 'room', 'created_by')
        }),
        ('Priority & Status', {
            'fields': ('priority', 'status')
        }),
        ('Scheduling', {
            'fields': ('requested_date', 'scheduled_date', 'completed_date')
        }),
        ('Assignment', {
            'fields': ('assigned_to', 'assigned_date')
        }),
        ('Cost Tracking', {
            'fields': ('estimated_cost', 'actual_cost'),
            'classes': ('collapse',)
        }),
        ('Resolution', {
            'fields': ('resolution_notes', 'resolution_photos'),
            'classes': ('collapse',)
        }),
        ('Follow-up', {
            'fields': ('follow_up_required', 'follow_up_date', 'follow_up_notes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def tenant_name(self, obj):
        return obj.tenant.name if obj.tenant else "-"
    tenant_name.short_description = "Tenant"
    tenant_name.admin_order_field = 'tenant__name'

    def room_identifier(self, obj):
        return obj.room.room_number if obj.room else "-"
    room_identifier.short_description = "Room"
    room_identifier.admin_order_field = 'room__room_number'

    def is_overdue(self, obj):
        return obj.is_overdue
    is_overdue.boolean = True
    is_overdue.short_description = "Overdue"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('tenant', 'room__location', 'created_by')
