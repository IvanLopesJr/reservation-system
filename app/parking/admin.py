from django.contrib import admin
from .models import ParkingSpot


@admin.register(ParkingSpot)
class ParkingSpotAdmin(admin.ModelAdmin):
    list_display = ['code', 'type', 'status', 'created_at']
    list_filter = ['type', 'status']
    search_fields = ['code']
