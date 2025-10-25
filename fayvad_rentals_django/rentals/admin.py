from django.contrib import admin
from .models import RentalAgreement

@admin.register(RentalAgreement)
class RentalAgreementAdmin(admin.ModelAdmin):
    """Admin for RentalAgreement model"""
    list_display = [
        'agreement_number', 'tenant_name', 'room_identifier',
        'status', 'start_date', 'end_date', 'rent_amount'
    ]
    list_filter = ['status', 'start_date', 'end_date', 'created_at']
    search_fields = [
        'agreement_number', 'tenant__name', 'tenant__email',
        'room__room_number', 'room__location__name'
    ]
    readonly_fields = ['agreement_number', 'created_at', 'updated_at']
    ordering = ['-created_at']

    fieldsets = (
        ('Agreement Information', {
            'fields': ('agreement_number', 'status')
        }),
        ('Parties', {
            'fields': ('tenant', 'room')
        }),
        ('Terms', {
            'fields': ('start_date', 'end_date', 'rent_amount', 'deposit_amount')
        }),
        ('Notice & Termination', {
            'fields': ('notice_given_date', 'notice_period_days')
        }),
        ('Additional Terms', {
            'fields': ('special_terms', 'security_deposit_returned', 'security_deposit_return_date'),
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

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('tenant', 'room__location')
