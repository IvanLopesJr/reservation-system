from django.contrib import admin
from .models import Room, RoomPosition


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name']


@admin.register(RoomPosition)
class RoomPositionAdmin(admin.ModelAdmin):
    list_display = ['code', 'room', 'status', 'created_at']
    list_filter = ['status', 'room']
    search_fields = ['code']
