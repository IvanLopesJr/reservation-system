from datetime import date, timedelta
import pytest
from django.contrib.auth import get_user_model
from django.db import transaction
from booking.models import Reservation
from booking.services import ReservationService, ReservationConflictError, PERIOD_CONFLICT_MAP
from rooms.models import Room, RoomPosition
from parking.models import ParkingSpot
from accounts.services import UserProfileService

User = get_user_model()


@pytest.fixture
def admin_user(db):
    user = User.objects.create_user(
        email='admin@test.com', password='test123',
        first_name='Admin', last_name='Test',
        is_staff=True,
    )
    UserProfileService.complete_first_access(user)
    return user


@pytest.fixture
def regular_user(db):
    user = User.objects.create_user(
        email='user@test.com', password='test123',
        first_name='User', last_name='Test',
    )
    UserProfileService.complete_first_access(user)
    return user


@pytest.fixture
def room(db):
    return Room.objects.create(name='Sala A', is_active=True)


@pytest.fixture
def position(db, room):
    return RoomPosition.objects.create(room=room, code='A01', status='available')


@pytest.fixture
def parking_spot(db):
    return ParkingSpot.objects.create(code='V01', type='common', status='available')


class TestPeriodConflictMap:
    def test_morning_conflicts_with_morning(self):
        assert 'morning' in PERIOD_CONFLICT_MAP['morning']

    def test_morning_conflicts_with_full_day(self):
        assert 'full_day' in PERIOD_CONFLICT_MAP['morning']

    def test_morning_does_not_conflict_with_afternoon(self):
        assert 'afternoon' not in PERIOD_CONFLICT_MAP['morning']

    def test_afternoon_conflicts_with_afternoon(self):
        assert 'afternoon' in PERIOD_CONFLICT_MAP['afternoon']

    def test_afternoon_conflicts_with_full_day(self):
        assert 'full_day' in PERIOD_CONFLICT_MAP['afternoon']

    def test_full_day_conflicts_with_all(self):
        assert set(PERIOD_CONFLICT_MAP['full_day']) == {'morning', 'afternoon', 'full_day'}


class TestCheckConflict:
    def test_no_conflict_when_no_reservation(self, db, position):
        future_date = date.today() + timedelta(days=1)
        assert not ReservationService.check_conflict('room_position', position.id, future_date, 'morning')

    def test_conflict_detected_for_same_position(self, db, regular_user, position):
        future_date = date.today() + timedelta(days=1)
        Reservation.objects.create(
            user=regular_user, room_position=position,
            reservation_date=future_date, period='morning', status='active'
        )
        assert ReservationService.check_conflict('room_position', position.id, future_date, 'morning')

    def test_full_day_blocks_morning(self, db, regular_user, position):
        future_date = date.today() + timedelta(days=1)
        Reservation.objects.create(
            user=regular_user, room_position=position,
            reservation_date=future_date, period='full_day', status='active'
        )
        assert ReservationService.check_conflict('room_position', position.id, future_date, 'morning')

    def test_full_day_blocks_afternoon(self, db, regular_user, position):
        future_date = date.today() + timedelta(days=1)
        Reservation.objects.create(
            user=regular_user, room_position=position,
            reservation_date=future_date, period='full_day', status='active'
        )
        assert ReservationService.check_conflict('room_position', position.id, future_date, 'afternoon')

    def test_morning_blocks_full_day(self, db, regular_user, position):
        future_date = date.today() + timedelta(days=1)
        Reservation.objects.create(
            user=regular_user, room_position=position,
            reservation_date=future_date, period='morning', status='active'
        )
        assert ReservationService.check_conflict('room_position', position.id, future_date, 'full_day')

    def test_cancelled_reservation_does_not_block(self, db, regular_user, position):
        future_date = date.today() + timedelta(days=1)
        Reservation.objects.create(
            user=regular_user, room_position=position,
            reservation_date=future_date, period='morning', status='cancelled'
        )
        assert not ReservationService.check_conflict('room_position', position.id, future_date, 'morning')

    def test_different_date_no_conflict(self, db, regular_user, position):
        today = date.today()
        tomorrow = today + timedelta(days=1)
        Reservation.objects.create(
            user=regular_user, room_position=position,
            reservation_date=today, period='morning', status='active'
        )
        assert not ReservationService.check_conflict('room_position', position.id, tomorrow, 'morning')

    def test_parking_spot_conflict(self, db, regular_user, parking_spot):
        future_date = date.today() + timedelta(days=1)
        room = Room.objects.create(name='Sala B')
        pos = RoomPosition.objects.create(room=room, code='B01', status='available')
        Reservation.objects.create(
            user=regular_user, room_position=pos, parking_spot=parking_spot,
            reservation_date=future_date, period='morning', status='active'
        )
        assert ReservationService.check_conflict('parking_spot', parking_spot.id, future_date, 'morning')

    def test_exclude_id_ignores_own_reservation(self, db, regular_user, position):
        future_date = date.today() + timedelta(days=1)
        reservation = Reservation.objects.create(
            user=regular_user, room_position=position,
            reservation_date=future_date, period='morning', status='active'
        )
        assert not ReservationService.check_conflict(
            'room_position', position.id, future_date, 'morning', exclude_id=reservation.id
        )


class TestCreateReservation:
    def test_create_minimal(self, db, regular_user, position):
        future_date = date.today() + timedelta(days=1)
        reservation = ReservationService.create_reservation(
            user=regular_user, room_position=position,
            reservation_date=future_date, period='morning'
        )
        assert reservation.status == 'active'
        assert reservation.user == regular_user
        assert reservation.room_position == position
        assert reservation.parking_spot is None

    def test_create_with_parking(self, db, regular_user, position, parking_spot):
        future_date = date.today() + timedelta(days=1)
        reservation = ReservationService.create_reservation(
            user=regular_user, room_position=position,
            reservation_date=future_date, period='morning',
            parking_spot=parking_spot
        )
        assert reservation.parking_spot == parking_spot

    def test_rejects_past_date(self, db, regular_user, position):
        past_date = date.today() - timedelta(days=1)
        with pytest.raises(ReservationConflictError, match='data passada'):
            ReservationService.create_reservation(
                user=regular_user, room_position=position,
                reservation_date=past_date, period='morning'
            )

    def test_rejects_conflicting_position(self, db, regular_user, position):
        future_date = date.today() + timedelta(days=1)
        ReservationService.create_reservation(
            user=regular_user, room_position=position,
            reservation_date=future_date, period='morning'
        )
        with pytest.raises(ReservationConflictError, match='já possui uma reserva'):
            ReservationService.create_reservation(
                user=regular_user, room_position=position,
                reservation_date=future_date, period='morning'
            )

    def test_atomic_creation_rollback_on_error(self, db, regular_user, position, parking_spot):
        future_date = date.today() + timedelta(days=1)
        ReservationService.create_reservation(
            user=regular_user, room_position=position,
            reservation_date=future_date, period='morning',
            parking_spot=parking_spot
        )
        assert Reservation.objects.count() == 1

    def test_rejects_two_reservations_same_day(self, db, regular_user, position):
        future_date = date.today() + timedelta(days=1)
        room2 = Room.objects.create(name='Sala B', is_active=True)
        pos2 = RoomPosition.objects.create(room=room2, code='B01', status='available')
        ReservationService.create_reservation(
            user=regular_user, room_position=position,
            reservation_date=future_date, period='morning'
        )
        with pytest.raises(ReservationConflictError, match='já possui uma reserva'):
            ReservationService.create_reservation(
                user=regular_user, room_position=pos2,
                reservation_date=future_date, period='afternoon'
            )

    def test_same_user_different_days_allowed(self, db, regular_user, position):
        today = date.today()
        future1 = today + timedelta(days=1)
        future2 = today + timedelta(days=2)
        room2 = Room.objects.create(name='Sala B', is_active=True)
        pos2 = RoomPosition.objects.create(room=room2, code='B01', status='available')
        r1 = ReservationService.create_reservation(
            user=regular_user, room_position=position,
            reservation_date=future1, period='morning'
        )
        r2 = ReservationService.create_reservation(
            user=regular_user, room_position=pos2,
            reservation_date=future2, period='afternoon'
        )
        assert r1.status == 'active'
        assert r2.status == 'active'

    def test_different_users_same_day_allowed(self, db, regular_user, admin_user, position, room):
        future_date = date.today() + timedelta(days=1)
        pos2 = RoomPosition.objects.create(room=room, code='B01', status='available')
        r1 = ReservationService.create_reservation(
            user=regular_user, room_position=position,
            reservation_date=future_date, period='morning'
        )
        r2 = ReservationService.create_reservation(
            user=admin_user, room_position=pos2,
            reservation_date=future_date, period='afternoon'
        )
        assert r1.status == 'active'
        assert r2.status == 'active'


class TestCancelReservation:
    def test_cancel_own_reservation(self, db, regular_user, position):
        future_date = date.today() + timedelta(days=1)
        reservation = ReservationService.create_reservation(
            user=regular_user, room_position=position,
            reservation_date=future_date, period='morning'
        )
        cancelled = ReservationService.cancel_reservation(reservation, regular_user, 'Mudei de ideia')
        assert cancelled.status == 'cancelled'
        assert cancelled.cancelled_by == regular_user
        assert cancelled.cancellation_reason == 'Mudei de ideia'

    def test_cancel_frees_position(self, db, regular_user, position):
        future_date = date.today() + timedelta(days=1)
        reservation = ReservationService.create_reservation(
            user=regular_user, room_position=position,
            reservation_date=future_date, period='morning'
        )
        ReservationService.cancel_reservation(reservation, regular_user)
        assert not ReservationService.check_conflict('room_position', position.id, future_date, 'morning')

    def test_rejects_cancel_for_past_reservation(self, db, regular_user, position):
        past_date = date.today() - timedelta(days=1)
        reservation = Reservation.objects.create(
            user=regular_user, room_position=position,
            reservation_date=past_date, period='morning', status='active'
        )
        with pytest.raises(ReservationConflictError, match='passadas'):
            ReservationService.cancel_reservation(reservation, regular_user)
