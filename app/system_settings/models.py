import os
import re
from django.core.exceptions import ValidationError
from django.db import models


def validate_hex_color(value):
    if not re.match(r'^#[0-9a-fA-F]{6}$', value):
        raise ValidationError(f'{value} não é uma cor hexadecimal válida. Use o formato #RRGGBB.')


def validate_image(value):
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.png', '.jpg', '.jpeg', '.svg', '.ico']
    if ext not in valid_extensions:
        raise ValidationError(f'Tipo de arquivo não permitido: {ext}')
    max_size = 2 * 1024 * 1024
    if value.size > max_size:
        raise ValidationError(f'Arquivo muito grande (máximo 2MB).')


class SystemSettings(models.Model):
    app_name = models.CharField(max_length=100, default='Sistema de Reservas', verbose_name='Nome da aplicação')
    app_base_url = models.URLField(blank=True, verbose_name='URL base da aplicação')
    logo = models.ImageField(
        upload_to='logos/', blank=True, null=True,
        validators=[validate_image], verbose_name='Logo'
    )
    favicon = models.ImageField(
        upload_to='favicons/', blank=True, null=True,
        validators=[validate_image], verbose_name='Favicon'
    )
    login_image = models.ImageField(
        upload_to='login/', blank=True, null=True,
        validators=[validate_image], verbose_name='Imagem de login'
    )
    primary_color = models.CharField(max_length=7, default='#4f46e5', validators=[validate_hex_color], verbose_name='Cor primária')
    secondary_color = models.CharField(max_length=7, default='#f43f5e', validators=[validate_hex_color], verbose_name='Cor secundária')
    background_color = models.CharField(max_length=7, default='#f8fafc', validators=[validate_hex_color], verbose_name='Cor de fundo')
    navbar_bg_color = models.CharField(max_length=7, default='#4f46e5', validators=[validate_hex_color], verbose_name='Cor da barra de navegação')
    navbar_text_color = models.CharField(max_length=7, default='#ffffff', validators=[validate_hex_color], verbose_name='Cor do texto da barra de navegação')
    welcome_text = models.TextField(
        blank=True, default='Bem-vindo ao Sistema de Reservas', verbose_name='Texto de boas-vindas'
    )
    organization_name = models.CharField(max_length=100, blank=True, verbose_name='Nome da organização')
    support_email = models.EmailField(blank=True, verbose_name='E-mail de suporte')
    show_app_name_navbar = models.BooleanField(default=True, verbose_name='Exibir nome na barra de navegação')
    show_app_name_login = models.BooleanField(default=True, verbose_name='Exibir nome na tela de login')
    show_app_name_footer = models.BooleanField(default=True, verbose_name='Exibir nome no rodapé')
    use_offcanvas_nav = models.BooleanField(default=True, verbose_name='Usar menu offcanvas no celular')

    email_sender_name = models.CharField(max_length=100, blank=True, verbose_name='Nome do remetente')
    email_sender_address = models.EmailField(blank=True, verbose_name='E-mail remetente')
    email_reply_to = models.EmailField(blank=True, verbose_name='E-mail de resposta')
    smtp_host = models.CharField(max_length=200, blank=True, verbose_name='Host SMTP')
    smtp_port = models.IntegerField(default=587, verbose_name='Porta SMTP')
    smtp_username = models.CharField(max_length=200, blank=True, verbose_name='Usuário SMTP')
    smtp_password_encrypted = models.TextField(blank=True, verbose_name='Senha SMTP (criptografada)')
    smtp_use_tls = models.BooleanField(default=True, verbose_name='Usar TLS')
    smtp_use_ssl = models.BooleanField(default=False, verbose_name='Usar SSL')
    email_settings_active = models.BooleanField(default=False, verbose_name='Configuração de e-mail ativa')
    send_confirmation_email = models.BooleanField(default=True, verbose_name='Enviar e-mail ao confirmar reserva')
    send_cancellation_email = models.BooleanField(default=True, verbose_name='Enviar e-mail ao cancelar reserva')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Configuração do sistema'
        verbose_name_plural = 'Configurações do sistema'

    def save(self, *args, **kwargs):
        if self.smtp_use_tls and self.smtp_use_ssl:
            self.smtp_use_ssl = False
        if self.smtp_port == 465:
            if self.smtp_use_tls:
                self.smtp_use_tls = False
                self.smtp_use_ssl = True
            else:
                self.smtp_use_ssl = False
        elif self.smtp_use_ssl:
            self.smtp_use_ssl = False
        super().save(*args, **kwargs)

    def get_smtp_password(self):
        from .services import SystemSettingsService
        return SystemSettingsService.decrypt_password(self.smtp_password_encrypted)

    def set_smtp_password(self, raw_password):
        from .services import SystemSettingsService
        self.smtp_password_encrypted = SystemSettingsService.encrypt_password(raw_password)

    def __str__(self):
        return self.app_name
