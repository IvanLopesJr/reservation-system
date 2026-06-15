from django.db import models


class EmailLog(models.Model):
    class EmailType(models.TextChoices):
        ACCESS_INVITATION = 'access_invitation', 'Convite de acesso'
        PASSWORD_RESET = 'password_reset', 'Redefinição de senha'
        RESERVATION_CONFIRMATION = 'reservation_confirmation', 'Confirmação de reserva'
        RESERVATION_CANCELLED = 'reservation_cancelled', 'Cancelamento de reserva'
        SMTP_TEST = 'smtp_test', 'Teste SMTP'
        WELCOME_CREDENTIALS = 'welcome_credentials', 'Credenciais de boas-vindas'

    class Status(models.TextChoices):
        SENT = 'sent', 'Enviado'
        FAILED = 'failed', 'Falhou'
        PENDING = 'pending', 'Pendente'

    recipient = models.EmailField(verbose_name='Destinatário')
    subject = models.CharField(max_length=255, verbose_name='Assunto')
    email_type = models.CharField(max_length=30, choices=EmailType, verbose_name='Tipo de e-mail')
    status = models.CharField(max_length=10, choices=Status, verbose_name='Status')
    error_message = models.TextField(blank=True, verbose_name='Mensagem de erro')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Registro de e-mail'
        verbose_name_plural = 'Registros de e-mails'

    def __str__(self):
        return f'{self.get_email_type_display()} para {self.recipient} - {self.get_status_display()}'
