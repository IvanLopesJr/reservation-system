from django.db import models


class Room(models.Model):
    name = models.CharField(max_length=100, verbose_name='Nome')
    description = models.TextField(blank=True, verbose_name='Descrição')
    is_active = models.BooleanField(default=True, verbose_name='Ativo')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Sala'
        verbose_name_plural = 'Salas'

    def __str__(self):
        return self.name


class RoomPosition(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = 'available', 'Disponível'
        BLOCKED = 'blocked', 'Bloqueada'
        INACTIVE = 'inactive', 'Inativa'

    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='positions', verbose_name='Sala')
    code = models.CharField(max_length=10, verbose_name='Código')
    description = models.TextField(blank=True, verbose_name='Descrição')
    status = models.CharField(
        max_length=10, choices=Status, default=Status.AVAILABLE, verbose_name='Status'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Posição'
        verbose_name_plural = 'Posições'
        unique_together = ['room', 'code']

    def __str__(self):
        return f'{self.room.name} - {self.code}'
