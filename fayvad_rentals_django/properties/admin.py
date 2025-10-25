from django.contrib import admin
from .models import Location, Room

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    """Admin for Location model"""
    list_display = ['name', 'code', 'city', 'is_active', 'setup_complete', 'room_count', 'occupancy_rate']
    list_filter = ['is_active', 'setup_complete', 'city']
    search_fields = ['name', 'code', 'address']
    readonly_fields = ['created_at', 'updated_at', 'setup_date']
    ordering = ['name']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'address', 'city')
        }),
        ('Management', {
            'fields': ('manager', 'is_active')
        }),
        ('Setup Status', {
            'fields': ('setup_complete', 'setup_date'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def room_count(self, obj):
        return obj.room_count
    room_count.short_description = "Rooms"

    def occupancy_rate(self, obj):
        return f"{obj.occupancy_rate}%"
    occupancy_rate.short_description = "Occupancy"

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    """Admin for Room model"""
    list_display = ['full_room_identifier', 'location', 'room_type', 'capacity', 'status', 'current_tenant_name']
    list_filter = ['status', 'room_type', 'location', 'floor']
    search_fields = ['room_number', 'location__name', 'location__code']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['location', 'room_number']

    fieldsets = (
        ('Basic Information', {
            'fields': ('location', 'room_number', 'room_type', 'floor', 'capacity')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Description', {
            'fields': ('description',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def current_tenant_name(self, obj):
        active_agreement = obj.rental_agreements.filter(status='active').first()
        return active_agreement.tenant.name if active_agreement else "-"
    current_tenant_name.short_description = "Current Tenant"
