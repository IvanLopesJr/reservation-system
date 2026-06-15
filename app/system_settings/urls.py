from django.urls import path
from . import views

app_name = 'system_settings'

urlpatterns = [
    path('', views.system_settings_view, name='settings'),
    path('testar-smtp/', views.smtp_test_view, name='smtp_test'),
    path('testar-config/', views.smtp_test_config_view, name='smtp_test_config'),
]
