from .services import SystemSettingsService


def theme_settings(request):
    try:
        settings_obj = SystemSettingsService.get_settings()
    except Exception:
        settings_obj = None

    context = {
        'app_settings': settings_obj,
    }
    return context
