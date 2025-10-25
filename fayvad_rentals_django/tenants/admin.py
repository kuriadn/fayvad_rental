"""
Tenant admin configuration
Preserves all functionality from FastAPI tenant management
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Tenant

@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    """Admin interface for Tenant model"""

    # List display
    list_display = [
        'name', 'email', 'phone', 'tenant_status', 'tenant_type',
        'compliance_status', 'account_balance', 'created_at'
    ]

    # List filters
    list_filter = [
        'tenant_status', 'compliance_status', 'tenant_type',
        'created_at', 'updated_at'
    ]

    # Search fields
    search_fields = [
        'name', 'email', 'phone', 'id_number',
        'emergency_contact_name', 'institution_employer'
    ]

    # Ordering
    ordering = ['-created_at']

    # Read-only fields
    readonly_fields = ['id', 'created_at', 'updated_at']

    # Fieldsets for form organization
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'email', 'phone', 'id_number')
        }),
        ('Contact Information', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone')
        }),
        ('Business Details', {
            'fields': ('tenant_type', 'institution_employer')
        }),
        ('Status & Compliance', {
            'fields': ('tenant_status', 'compliance_status', 'compliance_notes')
        }),
        ('Financial', {
            'fields': ('account_balance',)
        }),
        ('Associations', {
            'fields': ('user',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    # Custom methods for list display
    def get_queryset(self, request):
        """Optimize queryset for admin"""
        return super().get_queryset(request).select_related('user')

    def colored_status(self, obj):
        """Display status with color coding"""
        colors = {
            'prospective': 'blue',
            'active': 'green',
            'former': 'gray',
            'blacklisted': 'red',
        }
        color = colors.get(obj.tenant_status, 'black')
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            obj.get_tenant_status_display()
        )
    colored_status.short_description = 'Status'

    def colored_compliance(self, obj):
        """Display compliance status with color coding"""
        colors = {
            'compliant': 'green',
            'warning': 'orange',
            'violation': 'red',
        }
        color = colors.get(obj.compliance_status, 'black')
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            obj.get_compliance_status_display()
        )
    colored_compliance.short_description = 'Compliance'

    # Actions
    actions = ['mark_as_active', 'mark_as_former', 'update_compliance_status']

    def mark_as_active(self, request, queryset):
        """Mark selected tenants as active"""
        updated = queryset.update(tenant_status='active')
        self.message_user(
            request,
            f'{updated} tenant(s) marked as active.'
        )
    mark_as_active.short_description = "Mark selected tenants as active"

    def mark_as_former(self, request, queryset):
        """Mark selected tenants as former"""
        updated = queryset.update(tenant_status='former')
        self.message_user(
            request,
            f'{updated} tenant(s) marked as former.'
        )
    mark_as_former.short_description = "Mark selected tenants as former"

    def update_compliance_status(self, request, queryset):
        """Update compliance status for selected tenants"""
        # This would typically open a form, but for simplicity:
        updated = queryset.update(compliance_status='compliant')
        self.message_user(
            request,
            f'{updated} tenant(s) updated to compliant status.'
        )
    update_compliance_status.short_description = "Update compliance status"