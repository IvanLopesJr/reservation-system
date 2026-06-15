from cryptography.fernet import Fernet
from django.conf import settings


class SystemSettingsService:

    @staticmethod
    def get_fernet():
        key = settings.SMTP_PASSWORD_KEY
        if not key:
            return None
        try:
            if isinstance(key, str):
                key = key.encode()
            return Fernet(key)
        except Exception:
            return None

    @staticmethod
    def encrypt_password(raw_password):
        if not raw_password:
            return ''
        f = SystemSettingsService.get_fernet()
        if not f:
            return ''
        if isinstance(raw_password, str):
            raw_password = raw_password.encode()
        return f.encrypt(raw_password).decode()

    @staticmethod
    def decrypt_password(encrypted_password):
        if not encrypted_password:
            return ''
        f = SystemSettingsService.get_fernet()
        if not f:
            return ''
        try:
            if isinstance(encrypted_password, str):
                encrypted_password = encrypted_password.encode()
            return f.decrypt(encrypted_password).decode()
        except Exception:
            return ''

    @staticmethod
    def get_settings():
        from .models import SystemSettings
        try:
            settings_obj = SystemSettings.objects.first()
            if not settings_obj:
                settings_obj = SystemSettings.objects.create()
            return settings_obj
        except Exception:
            return None
