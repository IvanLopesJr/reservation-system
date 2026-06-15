from django.contrib import admin
from .models import EmailLog


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'email_type', 'status', 'created_at']
    list_filter = ['email_type', 'status']
    search_fields = ['recipient']
    date_hierarchy = 'created_at'
