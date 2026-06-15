from django.contrib import admin
from .models import Reservation


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['user', 'room_position', 'reservation_date', 'period', 'status', 'parking_spot', 'created_at']
    list_filter = ['status', 'period', 'reservation_date']
    search_fields = ['user__email', 'room_position__code']
    date_hierarchy = 'reservation_date'
