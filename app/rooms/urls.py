from django.urls import path
from . import views

app_name = 'rooms'

urlpatterns = [
    path('', views.room_list_view, name='room_list'),
    path('novo/', views.room_create_view, name='room_create'),
    path('<int:room_id>/editar/', views.room_update_view, name='room_update'),
    path('<int:room_id>/ativar/', views.room_toggle_active_view, name='room_toggle_active'),
    path('<int:room_id>/excluir/', views.room_delete_view, name='room_delete'),
    path('<int:room_id>/posicoes/', views.position_list_view, name='position_list'),
    path('<int:room_id>/posicoes/nova/', views.position_create_view, name='position_create'),
    path('<int:room_id>/posicoes/<int:pk>/editar/', views.position_update_view, name='position_update'),
    path('<int:room_id>/posicoes/<int:pk>/status/', views.position_toggle_status_view, name='position_toggle_status'),
    path('<int:room_id>/posicoes/<int:pk>/excluir/', views.position_delete_view, name='position_delete'),
]
