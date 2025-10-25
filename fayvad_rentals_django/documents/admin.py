from django.contrib import admin
from .models import Document

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """Admin for Document model"""
    list_display = [
        'title', 'document_type', 'tenant_name', 'room_identifier',
        'status', 'file_extension', 'size_mb', 'created_at'
    ]
    list_filter = ['document_type', 'status', 'is_required', 'created_at', 'uploaded_by']
    search_fields = [
        'title', 'description', 'filename',
        'tenant__name', 'tenant__email',
        'room__room_number', 'room__location__name'
    ]
    readonly_fields = ['file_url', 'size_mb', 'created_at', 'updated_at']
    ordering = ['-created_at']

    fieldsets = (
        ('Document Information', {
            'fields': ('title', 'document_type', 'description')
        }),
        ('File Information', {
            'fields': ('file', 'filename', 'file_url', 'size_mb'),
            'classes': ('collapse',)
        }),
        ('Related Entities', {
            'fields': ('tenant', 'rental_agreement', 'room')
        }),
        ('Status & Metadata', {
            'fields': ('status', 'is_required', 'reference_count')
        }),
        ('Organization', {
            'fields': ('tags', 'version'),
            'classes': ('collapse',)
        }),
        ('Access Control', {
            'fields': ('is_public', 'access_permissions'),
            'classes': ('collapse',)
        }),
        ('Audit', {
            'fields': ('uploaded_by', 'reviewed_by', 'reviewed_date'),
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

    def size_mb(self, obj):
        return ".2f"
    size_mb.short_description = "Size (MB)"
    size_mb.admin_order_field = 'file_size'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('tenant', 'rental_agreement', 'room', 'uploaded_by')
