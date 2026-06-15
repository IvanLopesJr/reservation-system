from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'entity_type', 'created_at']
    list_filter = ['action', 'entity_type']
    search_fields = ['user__email', 'action']
    date_hierarchy = 'created_at'
