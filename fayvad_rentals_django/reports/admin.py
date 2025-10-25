from django.contrib import admin
from .models import ReportTemplate, GeneratedReport

@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    """Admin for ReportTemplate model"""
    list_display = ['name', 'report_type', 'is_active', 'is_default', 'created_by', 'created_at']
    list_filter = ['report_type', 'is_active', 'is_default', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Template Information', {
            'fields': ('name', 'report_type', 'description')
        }),
        ('Configuration', {
            'fields': ('config', 'default_filters', 'available_formats')
        }),
        ('Settings', {
            'fields': ('is_active', 'is_default')
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


@admin.register(GeneratedReport)
class GeneratedReportAdmin(admin.ModelAdmin):
    """Admin for GeneratedReport model"""
    list_display = ['title', 'report_type', 'export_format', 'is_complete', 'generated_by', 'created_at']
    list_filter = ['report_type', 'export_format', 'is_complete', 'created_at']
    search_fields = ['title', 'error_message']
    readonly_fields = ['created_at', 'completed_at']

    fieldsets = (
        ('Report Information', {
            'fields': ('title', 'report_type', 'export_format')
        }),
        ('Generation', {
            'fields': ('filters_used', 'is_complete', 'error_message')
        }),
        ('File Storage', {
            'fields': ('file', 'file_size', 'report_data'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('generated_by', 'expires_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'completed_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('generated_by')
