import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from system_settings.models import SystemSettings
from .models import EmailLog

logger = logging.getLogger(__name__)


class EmailService:

    @staticmethod
    def get_active_config():
        try:
            settings_obj = SystemSettings.objects.first()
            if settings_obj and settings_obj.email_settings_active and settings_obj.smtp_host:
                return settings_obj
        except Exception:
            return None
        return None

    @staticmethod
    def build_email_backend(config):
        from django.core.mail.backends.smtp import EmailBackend
        try:
            password = config.get_smtp_password()
        except Exception:
            password = ''
        port = config.smtp_port
        use_tls_raw = config.smtp_use_tls or config.smtp_use_ssl
        if use_tls_raw:
            if port == 465:
                use_tls, use_ssl = False, True
            else:
                use_tls, use_ssl = True, False
        else:
            use_tls, use_ssl = False, False
        return EmailBackend(
            host=config.smtp_host, port=port, username=config.smtp_username,
            password=password, use_tls=use_tls, use_ssl=use_ssl,
            fail_silently=False,
        )

    @staticmethod
    def send_email(recipient, subject, template_name, context, email_type, config=None):
        if config is None:
            config = EmailService.get_active_config()
        if not config:
            log = EmailLog.objects.create(
                recipient=recipient,
                subject=subject,
                email_type=email_type,
                status='failed',
                error_message='SMTP não configurado ou inativo',
            )
            return log

        try:
            if config and config.organization_name:
                context.setdefault('organization_name', config.organization_name)
            html_content = render_to_string(template_name, context)
            text_content = strip_tags(html_content)

            sender = config.email_sender_address or settings.DEFAULT_FROM_EMAIL
            sender_name = config.email_sender_name or ''
            if sender_name:
                from_header = f'{sender_name} <{sender}>'
            else:
                from_header = sender

            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=from_header,
                to=[recipient],
                reply_to=[config.email_reply_to] if config.email_reply_to else [],
            )
            msg.attach_alternative(html_content, 'text/html')

            backend = EmailService.build_email_backend(config)
            msg.connection = backend
            msg.send()

            log = EmailLog.objects.create(
                recipient=recipient,
                subject=subject,
                email_type=email_type,
                status='sent',
            )
            return log

        except Exception as e:
            error_msg = str(e)
            logger.error(f'Falha ao enviar e-mail {email_type} para {recipient}: {error_msg[:200]}')
            log = EmailLog.objects.create(
                recipient=recipient,
                subject=subject,
                email_type=email_type,
                status='failed',
                error_message=error_msg[:500],
            )
            return log

    @staticmethod
    def send_invitation(user, invitation, base_url):
        from audit.services import AuditService
        token = getattr(invitation, '_plain_token', None)
        if not token:
            return None
        link = f'{base_url}/primeiro-acesso/{token}/'
        config = EmailService.get_active_config()
        app_name = getattr(config, 'app_name', 'Sistema de Reservas') if config else 'Sistema de Reservas'
        context = {
            'user': user,
            'app_name': app_name,
            'link': link,
            'support_email': getattr(config, 'support_email', '') if config else '',
            'expires_at': invitation.expires_at,
        }
        log = EmailService.send_email(
            recipient=user.email,
            subject=f'Convite de acesso - {app_name}',
            template_name='notifications/emails/invitation_email.html',
            context=context,
            email_type='access_invitation',
            config=config,
        )
        AuditService.log(
            user=getattr(invitation, 'created_by', None),
            action='enviar_convite',
            entity_type='AccessInvitation',
            entity_id=invitation.id,
            description=f'Convite enviado para {user.email}',
        )
        return log

    @staticmethod
    def send_password_reset(user, token, base_url):
        link = f'{base_url}/redefinir-senha/{token}/'
        config = EmailService.get_active_config()
        app_name = getattr(config, 'app_name', 'Sistema de Reservas') if config else 'Sistema de Reservas'
        context = {
            'user': user,
            'app_name': app_name,
            'link': link,
        }
        return EmailService.send_email(
            recipient=user.email,
            subject=f'Redefinição de senha - {app_name}',
            template_name='notifications/emails/password_reset_email.html',
            context=context,
            email_type='password_reset',
            config=config,
        )

    @staticmethod
    def send_reservation_confirmation(reservation):
        config = EmailService.get_active_config()
        if config and not config.send_confirmation_email:
            return None
        app_name = getattr(config, 'app_name', 'Sistema de Reservas') if config else 'Sistema de Reservas'
        context = {
            'reservation': reservation,
            'app_name': app_name,
            'period_display': reservation.get_period_display(),
        }
        return EmailService.send_email(
            recipient=reservation.user.email,
            subject=f'Reserva confirmada - {reservation.room_position.code} - {app_name}',
            template_name='notifications/emails/reservation_confirmation.html',
            context=context,
            email_type='reservation_confirmation',
            config=config,
        )

    @staticmethod
    def send_reservation_cancelled(reservation):
        config = EmailService.get_active_config()
        if config and not config.send_cancellation_email:
            return None
        app_name = getattr(config, 'app_name', 'Sistema de Reservas') if config else 'Sistema de Reservas'
        context = {
            'reservation': reservation,
            'app_name': app_name,
            'period_display': reservation.get_period_display(),
        }
        return EmailService.send_email(
            recipient=reservation.user.email,
            subject=f'Reserva cancelada - {reservation.room_position.code} - {app_name}',
            template_name='notifications/emails/reservation_cancelled.html',
            context=context,
            email_type='reservation_cancelled',
            config=config,
        )

    @staticmethod
    def send_welcome_credentials(user, raw_password):
        config = EmailService.get_active_config()
        app_name = getattr(config, 'app_name', 'Sistema de Reservas') if config else 'Sistema de Reservas'
        app_base_url = getattr(config, 'app_base_url', '') if config else ''
        context = {
            'user': user,
            'app_name': app_name,
            'app_base_url': app_base_url,
            'email': user.email,
            'password': raw_password,
            'support_email': getattr(config, 'support_email', '') if config else '',
        }
        return EmailService.send_email(
            recipient=user.email,
            subject=f'Bem-vindo(a) - Dados de acesso - {app_name}',
            template_name='notifications/emails/welcome_email.html',
            context=context,
            email_type='welcome_credentials',
            config=config,
        )

    @staticmethod
    def send_test_email(to_email, config):
        context = {
            'app_name': config.app_name or 'Sistema de Reservas',
            'host': config.smtp_host,
        }
        return EmailService.send_email(
            recipient=to_email,
            subject=f'Teste de e-mail - {config.app_name or "Sistema de Reservas"}',
            template_name='notifications/emails/smtp_test_email.html',
            context=context,
            email_type='smtp_test',
            config=config,
        )
