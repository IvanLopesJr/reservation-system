from datetime import date
from django.db import transaction
from django.utils import timezone
from parking.models import ParkingSpot
from rooms.models import RoomPosition
from .models import Reservation


PERIOD_CONFLICT_MAP = {
    'morning': ['morning', 'full_day'],
    'afternoon': ['afternoon', 'full_day'],
    'full_day': ['morning', 'afternoon', 'full_day'],
}


class ReservationConflictError(Exception):
    pass


class ReservationService:

    @staticmethod
    def get_conflicting_periods(period):
        return PERIOD_CONFLICT_MAP.get(period, [])

    @staticmethod
    def get_available_positions(room, reservation_date, period):
        conflicting_periods = PERIOD_CONFLICT_MAP[period]
        reserved_positions = Reservation.objects.filter(
            reservation_date=reservation_date,
            period__in=conflicting_periods,
            status='active',
            room_position__room=room,
        ).values_list('room_position_id', flat=True)

        return RoomPosition.objects.filter(
            room=room,
            status='available',
        ).exclude(id__in=reserved_positions)

    @staticmethod
    def get_available_parking_spots(reservation_date, period):
        conflicting_periods = PERIOD_CONFLICT_MAP[period]
        reserved_spots = Reservation.objects.filter(
            reservation_date=reservation_date,
            period__in=conflicting_periods,
            status='active',
            parking_spot__isnull=False,
        ).values_list('parking_spot_id', flat=True)

        return ParkingSpot.objects.filter(
            status='available',
        ).exclude(id__in=reserved_spots)

    @staticmethod
    def get_positions_with_occupancy(room, reservation_date, period):
        conflicting_periods = PERIOD_CONFLICT_MAP[period]

        reservations = Reservation.objects.filter(
            reservation_date=reservation_date,
            period__in=conflicting_periods,
            status='active',
            room_position__room=room,
        ).select_related('user', 'room_position', 'parking_spot')

        occupied = {r.room_position_id: r for r in reservations}
        positions = RoomPosition.objects.filter(room=room, status='available')

        result = []
        for pos in positions:
            entry = {'id': pos.id, 'code': pos.code, 'status': 'available'}
            if pos.id in occupied:
                r = occupied[pos.id]
                entry['status'] = 'occupied'
                entry['period'] = r.get_period_display()
                entry['user'] = r.user.get_full_name() or r.user.email
                entry['parking_code'] = r.parking_spot.code if r.parking_spot else None
            result.append(entry)

        return result

    @staticmethod
    def get_spots_with_occupancy(reservation_date, period):
        conflicting_periods = PERIOD_CONFLICT_MAP[period]

        reservations = Reservation.objects.filter(
            reservation_date=reservation_date,
            period__in=conflicting_periods,
            status='active',
            parking_spot__isnull=False,
        ).select_related('user', 'parking_spot')

        occupied = {r.parking_spot_id: r for r in reservations}
        spots = ParkingSpot.objects.filter(status='available')

        result = []
        for spot in spots:
            entry = {'id': spot.id, 'code': spot.code, 'status': 'available'}
            if spot.id in occupied:
                r = occupied[spot.id]
                entry['status'] = 'occupied'
                entry['period'] = r.get_period_display()
                entry['user'] = r.user.get_full_name() or r.user.email
            result.append(entry)

        return result

    @staticmethod
    def check_conflict(resource_type, resource_id, reservation_date, period, exclude_id=None):
        conflicting_periods = PERIOD_CONFLICT_MAP[period]
        filter_kwargs = {
            'reservation_date': reservation_date,
            'period__in': conflicting_periods,
            'status': 'active',
        }
        if resource_type == 'room_position':
            filter_kwargs['room_position_id'] = resource_id
        elif resource_type == 'parking_spot':
            filter_kwargs['parking_spot_id'] = resource_id
        else:
            raise ValueError(f'Tipo de recurso inválido: {resource_type}')

        qs = Reservation.objects.filter(**filter_kwargs)
        if exclude_id:
            qs = qs.exclude(id=exclude_id)
        return qs.exists()

    @staticmethod
    @transaction.atomic
    def create_reservation(user, room_position, reservation_date, period, parking_spot=None, created_by=None):
        if reservation_date < date.today():
            raise ReservationConflictError('Não é permitido reservar em data passada.')

        user_daily = Reservation.objects.select_for_update().filter(
            user=user,
            reservation_date=reservation_date,
            status='active',
        ).exists()
        if user_daily:
            raise ReservationConflictError('Você já possui uma reserva para esta data.')

        conflicting_periods = PERIOD_CONFLICT_MAP[period]

        position_conflict = Reservation.objects.select_for_update().filter(
            room_position=room_position,
            reservation_date=reservation_date,
            period__in=conflicting_periods,
            status='active',
        ).exists()

        if position_conflict:
            raise ReservationConflictError('Esta posição já está reservada para o período selecionado.')

        if parking_spot:
            spot_conflict = Reservation.objects.select_for_update().filter(
                parking_spot=parking_spot,
                reservation_date=reservation_date,
                period__in=conflicting_periods,
                status='active',
            ).exists()

            if spot_conflict:
                raise ReservationConflictError('Esta vaga de estacionamento já está reservada para o período selecionado.')

        reservation = Reservation.objects.create(
            user=user,
            room_position=room_position,
            parking_spot=parking_spot,
            reservation_date=reservation_date,
            period=period,
            status='active',
            created_by=created_by or user,
        )

        return reservation

    @staticmethod
    @transaction.atomic
    def cancel_reservation(reservation, cancelled_by, reason=''):
        now = timezone.now()
        if reservation.reservation_date < now.date():
            raise ReservationConflictError('Não é possível cancelar reservas passadas.')

        reservation.status = 'cancelled'
        reservation.cancelled_by = cancelled_by
        reservation.cancelled_at = now
        reservation.cancellation_reason = reason
        reservation.save(update_fields=['status', 'cancelled_by', 'cancelled_at', 'cancellation_reason', 'updated_at'])
        return reservation
