from datetime import date
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from booking.models import Reservation
from notifications.models import EmailLog
from rooms.models import RoomPosition
from parking.models import ParkingSpot


def handler403(request, exception):
    return render(request, 'errors/403.html', status=403)


def handler404(request, exception):
    return render(request, 'errors/404.html', status=404)


def handler500(request):
    return render(request, 'errors/500.html', status=500)


def is_admin(user):
    return user.is_authenticated and user.is_staff


@login_required
def dashboard_view(request):
    if request.user.is_staff:
        return admin_dashboard_view(request)
    return user_dashboard_view(request)


def user_dashboard_view(request):
    today = date.today()

    today_reservations = Reservation.objects.filter(
        reservation_date=today, status='active'
    ).select_related('user', 'room_position__room', 'parking_spot')

    total_positions = RoomPosition.objects.filter(status='available').count()
    total_spots = ParkingSpot.objects.filter(status='available').count()

    occupied_positions_count = today_reservations.values_list('room_position_id', flat=True).distinct().count()
    occupied_spots_count = today_reservations.exclude(parking_spot__isnull=True).values_list('parking_spot_id', flat=True).distinct().count()

    available_positions = total_positions - occupied_positions_count
    available_spots = total_spots - occupied_spots_count

    morning_reservations = today_reservations.filter(period='morning').count()
    afternoon_reservations = today_reservations.filter(period='afternoon').count()
    full_day_reservations = today_reservations.filter(period='full_day').count()

    available_morning = total_positions - (morning_reservations + full_day_reservations)
    available_afternoon = total_positions - (afternoon_reservations + full_day_reservations)
    available_full_day = total_positions - occupied_positions_count

    morning_parking_occupied = today_reservations.filter(period='morning').exclude(parking_spot__isnull=True).count()
    afternoon_parking_occupied = today_reservations.filter(period='afternoon').exclude(parking_spot__isnull=True).count()
    full_day_parking_occupied = today_reservations.filter(period='full_day').exclude(parking_spot__isnull=True).count()

    available_spots_morning = total_spots - (morning_parking_occupied + full_day_parking_occupied)
    available_spots_afternoon = total_spots - (afternoon_parking_occupied + full_day_parking_occupied)
    available_spots_full_day = total_spots - occupied_spots_count

    upcoming_reservations = Reservation.objects.filter(
        user=request.user,
        status='active',
        reservation_date__gt=today,
    ).select_related('room_position__room', 'parking_spot').order_by('reservation_date')[:5]

    next_reservation = upcoming_reservations.first() if upcoming_reservations else None

    context = {
        'today_reservations': today_reservations,
        'available_positions': available_positions,
        'available_spots': available_spots,
        'available_morning': available_morning,
        'available_afternoon': available_afternoon,
        'available_full_day': available_full_day,
        'available_spots_morning': available_spots_morning,
        'available_spots_afternoon': available_spots_afternoon,
        'available_spots_full_day': available_spots_full_day,
        'next_reservation': next_reservation,
        'upcoming_reservations': upcoming_reservations,
    }
    return render(request, 'core/user_dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def admin_dashboard_view(request):
    today = date.today()
    today_reservations = Reservation.objects.filter(
        reservation_date=today, status='active'
    ).select_related('user', 'room_position__room', 'parking_spot')

    total_positions = RoomPosition.objects.filter(status='available').count()
    total_spots = ParkingSpot.objects.filter(status='available').count()

    morning_count = today_reservations.filter(period='morning').count()
    afternoon_count = today_reservations.filter(period='afternoon').count()
    full_day_count = today_reservations.filter(period='full_day').count()
    parking_occupied_count = today_reservations.exclude(parking_spot__isnull=True).count()
    users_today = today_reservations.values_list('user_id', flat=True).distinct().count()

    occupied_total = morning_count + afternoon_count + full_day_count

    occupied_positions_count = today_reservations.values_list('room_position_id', flat=True).distinct().count()
    occupied_spots_count = today_reservations.exclude(parking_spot__isnull=True).values_list('parking_spot_id', flat=True).distinct().count()

    available_morning = total_positions - (morning_count + full_day_count)
    available_afternoon = total_positions - (afternoon_count + full_day_count)
    available_full_day = total_positions - occupied_positions_count

    morning_parking_occupied = today_reservations.filter(period='morning').exclude(parking_spot__isnull=True).count()
    afternoon_parking_occupied = today_reservations.filter(period='afternoon').exclude(parking_spot__isnull=True).count()
    full_day_parking_occupied = today_reservations.filter(period='full_day').exclude(parking_spot__isnull=True).count()

    available_spots_morning = total_spots - (morning_parking_occupied + full_day_parking_occupied)
    available_spots_afternoon = total_spots - (afternoon_parking_occupied + full_day_parking_occupied)
    available_spots_full_day = total_spots - occupied_spots_count

    recent_failures = EmailLog.objects.filter(
        status='failed'
    ).order_by('-created_at')[:5]

    context = {
        'today_reservations': today_reservations,
        'total_positions': total_positions,
        'total_spots': total_spots,
        'parking_occupied_count': parking_occupied_count,
        'occupied_total': occupied_total,
        'users_today': users_today,
        'available_morning': available_morning,
        'available_afternoon': available_afternoon,
        'available_full_day': available_full_day,
        'available_spots_morning': available_spots_morning,
        'available_spots_afternoon': available_spots_afternoon,
        'available_spots_full_day': available_spots_full_day,
        'recent_failures': recent_failures,
    }
    return render(request, 'core/admin_dashboard.html', context)
