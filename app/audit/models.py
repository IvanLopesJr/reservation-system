from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='Usuário'
    )
    action = models.CharField(max_length=100, verbose_name='Ação')
    entity_type = models.CharField(max_length=50, blank=True, verbose_name='Tipo de entidade')
    entity_id = models.PositiveIntegerField(null=True, blank=True, verbose_name='ID da entidade')
    description = models.TextField(blank=True, verbose_name='Descrição')
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name='Endereço IP')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Registro de auditoria'
        verbose_name_plural = 'Registros de auditoria'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.action} por {self.user} em {self.created_at:%d/%m/%Y %H:%M}'
