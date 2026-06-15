from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('primeiro-acesso/', views.first_access_required, name='first_access_required'),
    path('primeiro-acesso/<str:token>/', views.first_access_view, name='first_access'),
    path('redefinir-senha/', views.password_reset_request, name='password_reset'),
    path('redefinir-senha/<str:uidb64>/<str:token>/', views.password_reset_confirm_view, name='password_reset_confirm'),
    path('alterar-senha/', views.password_change_view, name='password_change'),
    path('app/usuarios/', views.user_list_view, name='user_list'),
    path('app/usuarios/novo/', views.user_create_view, name='user_create'),
    path('app/usuarios/<int:user_id>/editar/', views.user_update_view, name='user_update'),
    path('app/usuarios/<int:user_id>/ativar/', views.user_toggle_active_view, name='user_toggle_active'),
    path('app/usuarios/<int:user_id>/convidar/', views.resend_invitation_view, name='resend_invitation'),
    path('app/usuarios/<int:user_id>/reenviar-credenciais/', views.resend_credentials_view, name='resend_credentials'),
    path('app/usuarios/<int:user_id>/excluir/', views.user_delete_view, name='user_delete'),
]
