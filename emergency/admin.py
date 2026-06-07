from django.contrib import admin
from .models import SOSAlert, SafeZone

@admin.register(SOSAlert)
class SOSAlertAdmin(admin.ModelAdmin):
    list_display = ('user', 'emergency_type', 'status', 'address', 'created_at')
    list_filter = ('status', 'emergency_type')
    readonly_fields = ('ai_dispatch_note', 'created_at', 'updated_at')

@admin.register(SafeZone)
class SafeZoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'zone_type', 'address', 'phone', 'is_active')
    list_filter = ('zone_type', 'is_active')
    list_editable = ('is_active',)
