from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from core.views import handler403, handler404, handler500


handler403 = handler403
handler404 = handler404
handler500 = handler500

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('', include('accounts.urls')),
    path('app/salas/', include('rooms.urls')),
    path('app/vagas/', include('parking.urls')),
    path('app/reservas/', include('booking.urls')),
    path('app/configuracoes/', include('system_settings.urls')),
    path('app/auditoria/', include('audit.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
