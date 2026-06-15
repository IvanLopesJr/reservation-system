import pytest
from django.contrib.auth import get_user_model
from notifications.models import EmailLog
from system_settings.models import SystemSettings
from system_settings.services import SystemSettingsService

User = get_user_model()


class TestSystemSettingsService:
    def test_encrypt_decrypt_password(self, db):
        original = 'my-smtp-password-123'
        encrypted = SystemSettingsService.encrypt_password(original)
        assert encrypted != original
        assert encrypted != ''
        decrypted = SystemSettingsService.decrypt_password(encrypted)
        assert decrypted == original

    def test_empty_password_returns_empty(self, db):
        assert SystemSettingsService.encrypt_password('') == ''
        assert SystemSettingsService.decrypt_password('') == ''

    def test_get_settings_creates_default(self, db):
        settings = SystemSettingsService.get_settings()
        assert settings is not None
        assert settings.app_name == 'Sistema de Reservas'


class TestSystemSettingsModel:
    def test_tls_and_ssl_mutually_exclusive(self, db):
        settings = SystemSettings.objects.create(
            smtp_use_tls=True, smtp_use_ssl=True
        )
        settings.save()
        settings.refresh_from_db()
        assert settings.smtp_use_tls is True
        assert settings.smtp_use_ssl is False

    def test_set_and_get_smtp_password(self, db):
        settings = SystemSettingsService.get_settings()
        settings.set_smtp_password('secret123')
        settings.save()
        settings.refresh_from_db()
        assert settings.get_smtp_password() == 'secret123'
        assert settings.smtp_password_encrypted != 'secret123'


class TestEmailLog:
    def test_create_email_log(self, db):
        log = EmailLog.objects.create(
            recipient='user@test.com',
            subject='Teste',
            email_type='smtp_test',
            status='sent',
        )
        assert log.id is not None
        assert log.status == 'sent'
