from django.urls import path
from . import views

app_name = 'parking'

urlpatterns = [
    path('', views.parking_spot_list_view, name='parking_spot_list'),
    path('nova/', views.parking_spot_create_view, name='parking_spot_create'),
    path('<int:spot_id>/editar/', views.parking_spot_update_view, name='parking_spot_update'),
    path('<int:spot_id>/status/', views.parking_spot_toggle_status_view, name='parking_spot_toggle_status'),
    path('<int:spot_id>/excluir/', views.parking_spot_delete_view, name='parking_spot_delete'),
]
