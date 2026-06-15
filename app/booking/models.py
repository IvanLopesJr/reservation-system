from django.conf import settings
from django.db import models


class Reservation(models.Model):
    class Period(models.TextChoices):
        MORNING = 'morning', 'Manhã'
        AFTERNOON = 'afternoon', 'Tarde'
        FULL_DAY = 'full_day', 'Dia inteiro'

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Ativa'
        CANCELLED = 'cancelled', 'Cancelada'
        FINISHED = 'finished', 'Finalizada'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='reservations', verbose_name='Usuário'
    )
    room_position = models.ForeignKey(
        'rooms.RoomPosition', on_delete=models.PROTECT,
        related_name='reservations', verbose_name='Posição'
    )
    parking_spot = models.ForeignKey(
        'parking.ParkingSpot', on_delete=models.PROTECT,
        null=True, blank=True, related_name='reservations',
        verbose_name='Vaga de estacionamento'
    )
    reservation_date = models.DateField(verbose_name='Data da reserva')
    period = models.CharField(max_length=10, choices=Period, verbose_name='Período')
    status = models.CharField(
        max_length=10, choices=Status, default=Status.ACTIVE, verbose_name='Status'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='created_reservations',
        verbose_name='Criado por'
    )
    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='cancelled_reservations',
        verbose_name='Cancelado por'
    )
    cancelled_at = models.DateTimeField(null=True, blank=True, verbose_name='Cancelado em')
    cancellation_reason = models.TextField(blank=True, verbose_name='Motivo do cancelamento')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        indexes = [
            models.Index(fields=['reservation_date', 'period', 'status']),
            models.Index(fields=['room_position']),
            models.Index(fields=['parking_spot']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f'{self.user.email} - {self.room_position} - {self.reservation_date} ({self.get_period_display()})'
