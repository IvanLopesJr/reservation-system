from django.db import models


class ParkingSpot(models.Model):
    class Type(models.TextChoices):
        COMMON = 'common', 'Comum'
        ACCESSIBLE = 'accessible', 'Acessível'
        VISITOR = 'visitor', 'Visitante'
        RESERVED = 'reserved', 'Reservada'

    class Status(models.TextChoices):
        AVAILABLE = 'available', 'Disponível'
        BLOCKED = 'blocked', 'Bloqueada'
        INACTIVE = 'inactive', 'Inativa'

    code = models.CharField(max_length=10, unique=True, verbose_name='Código')
    type = models.CharField(max_length=10, choices=Type, default=Type.COMMON, verbose_name='Tipo')
    description = models.TextField(blank=True, verbose_name='Descrição')
    status = models.CharField(
        max_length=10, choices=Status, default=Status.AVAILABLE, verbose_name='Status'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Vaga de estacionamento'
        verbose_name_plural = 'Vagas de estacionamento'

    def __str__(self):
        return f'{self.code} ({self.get_type_display()})'
