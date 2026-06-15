from django.urls import path
from . import views

app_name = 'booking'

urlpatterns = [
    path('nova/', views.reservation_create_view, name='reservation_create'),
    path('posicoes-disponiveis/', views.available_positions_view, name='available_positions'),
    path('vagas-disponiveis/', views.available_parking_spots_view, name='available_parking_spots'),
    path('minhas-reservas/', views.my_reservations_view, name='my_reservations'),
    path('minhas-reservas/<int:reservation_id>/', views.reservation_detail_view, name='reservation_detail'),
    path('minhas-reservas/<int:reservation_id>/cancelar/', views.reservation_cancel_view, name='reservation_cancel'),
    path('admin/', views.admin_reservations_view, name='admin_reservations'),
    path('admin/<int:reservation_id>/cancelar/', views.reservation_cancel_view, name='admin_reservation_cancel'),
    path('admin/exportar/', views.reservation_export_view, name='reservation_export'),
]
