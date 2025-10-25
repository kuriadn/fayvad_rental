from django.contrib import admin
from .models import Dashboard, KPI

@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    """Admin for Dashboard model"""
    list_display = ['name', 'dashboard_type', 'is_active', 'is_default', 'created_by', 'created_at']
    list_filter = ['dashboard_type', 'is_active', 'is_default', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Dashboard Information', {
            'fields': ('name', 'dashboard_type', 'description')
        }),
        ('Configuration', {
            'fields': ('is_active', 'is_default', 'config')
        }),
        ('Metadata', {
            'fields': ('created_by',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by')


@admin.register(KPI)
class KPIAdmin(admin.ModelAdmin):
    """Admin for KPI model"""
    list_display = ['name', 'code', 'metric_type', 'category', 'status', 'is_active']
    list_filter = ['metric_type', 'is_active', 'category', 'dashboard_types']
    search_fields = ['name', 'code', 'description']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('KPI Information', {
            'fields': ('name', 'code', 'description', 'category')
        }),
        ('Metric Configuration', {
            'fields': ('metric_type', 'model_name', 'field_name', 'filters')
        }),
        ('Display', {
            'fields': ('unit', 'format_string'),
            'classes': ('collapse',)
        }),
        ('Thresholds', {
            'fields': ('target_value', 'warning_threshold', 'critical_threshold'),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('is_active', 'dashboard_types')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def status(self, obj):
        return obj.status
    status.short_description = "Status"
