from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin for Payment model"""
    list_display = [
        'payment_number', 'tenant_name', 'amount', 'payment_method',
        'status', 'payment_date', 'created_at'
    ]
    list_filter = ['status', 'payment_method', 'payment_date', 'created_at']
    search_fields = [
        'payment_number', 'reference_number', 'transaction_id',
        'tenant__name', 'tenant__email'
    ]
    readonly_fields = ['payment_number', 'created_at', 'updated_at', 'processed_date']
    ordering = ['-created_at']

    fieldsets = (
        ('Payment Information', {
            'fields': ('payment_number', 'amount', 'payment_method', 'reference_number')
        }),
        ('Related Entities', {
            'fields': ('tenant', 'rental_agreement', 'room')
        }),
        ('Status & Dates', {
            'fields': ('status', 'payment_date', 'processed_date')
        }),
        ('Details', {
            'fields': ('notes', 'description', 'transaction_id', 'processor_response'),
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

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('tenant', 'rental_agreement', 'room')
