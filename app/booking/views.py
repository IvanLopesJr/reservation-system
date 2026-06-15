import csv
from datetime import date, datetime, timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from audit.services import AuditService
from notifications.services import EmailService
from rooms.models import Room
from .forms import ReservationForm, ReservationCancelForm
from .models import Reservation
from .services import ReservationService, ReservationConflictError


def is_admin(user):
    return user.is_authenticated and user.is_staff


@login_required
def reservation_create_view(request):
    rooms = Room.objects.filter(is_active=True)
    today_str = str(date.today())
    form = ReservationForm(min_date=today_str)

    if request.method == 'POST':
        form = ReservationForm(request.POST, min_date=today_str)
        if form.is_valid():
            data = form.cleaned_data
            try:
                position = data['room_position']
                parking_spot = data.get('parking_spot') if data.get('wants_parking') else None

                reservation = ReservationService.create_reservation(
                    user=request.user,
                    room_position=position,
                    reservation_date=data['reservation_date'],
                    period=data['period'],
                    parking_spot=parking_spot,
                )

                try:
                    EmailService.send_reservation_confirmation(reservation)
                except Exception:
                    messages.warning(request, 'Reserva criada, mas o e-mail de confirmação não pôde ser enviado.')

                messages.success(request, 'Reserva criada com sucesso!')
                return redirect('booking:my_reservations')

            except ReservationConflictError as e:
                messages.error(request, str(e))
            except Exception as e:
                messages.error(request, f'Erro ao criar reserva: {str(e)}')

    context = {
        'form': form,
        'rooms': rooms,
        'min_date': today_str,
    }
    return render(request, 'booking/reservation_form.html', context)


@login_required
def available_positions_view(request):
    date_str = request.GET.get('date')
    period = request.GET.get('period')
    room_id = request.GET.get('room')

    if not all([date_str, period, room_id]):
        return JsonResponse({'positions': []})

    try:
        reservation_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'positions': []})

    room = get_object_or_404(Room, id=room_id)
    data = ReservationService.get_positions_with_occupancy(room, reservation_date, period)
    return JsonResponse({'positions': data})


@login_required
def available_parking_spots_view(request):
    profile = getattr(request.user, 'profile', None)
    if profile and not profile.can_use_parking:
        return JsonResponse({'spots': [], 'blocked': True})

    date_str = request.GET.get('date')
    period = request.GET.get('period')

    if not all([date_str, period]):
        return JsonResponse({'spots': []})

    try:
        reservation_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'spots': []})

    data = ReservationService.get_spots_with_occupancy(reservation_date, period)
    return JsonResponse({'spots': data})


@login_required
def my_reservations_view(request):
    reservations = Reservation.objects.filter(user=request.user).select_related(
        'room_position__room', 'parking_spot'
    ).order_by('-reservation_date', '-created_at')
    return render(request, 'booking/my_reservations.html', {'reservations': reservations, 'today': date.today()})


@login_required
def reservation_detail_view(request, reservation_id):
    reservation = get_object_or_404(
        Reservation.objects.select_related('room_position__room', 'parking_spot', 'user'),
        id=reservation_id
    )
    if not request.user.is_staff and reservation.user != request.user:
        messages.error(request, 'Você não tem permissão para ver esta reserva.')
        return redirect('booking:my_reservations')
    return render(request, 'booking/reservation_detail.html', {'reservation': reservation})


@login_required
def reservation_cancel_view(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    if not request.user.is_staff and reservation.user != request.user:
        messages.error(request, 'Você não tem permissão para cancelar esta reserva.')
        return redirect('booking:my_reservations')

    if request.method == 'POST':
        form = ReservationCancelForm(request.POST)
        reason = ''
        if form.is_valid():
            reason = form.cleaned_data.get('reason', '')

        try:
            ReservationService.cancel_reservation(reservation, request.user, reason)
            try:
                EmailService.send_reservation_cancelled(reservation)
            except Exception:
                pass
            AuditService.log_reservation_cancelled(reservation, request.user, request)
            messages.success(request, 'Reserva cancelada com sucesso.')
        except ReservationConflictError as e:
            messages.error(request, str(e))

        if request.user.is_staff:
            return redirect('booking:admin_reservations')
        return redirect('booking:my_reservations')

    form = ReservationCancelForm()
    return render(request, 'booking/reservation_cancel_confirm.html', {
        'reservation': reservation,
        'form': form,
    })


@login_required
@user_passes_test(is_admin)
def admin_reservations_view(request):
    reservations = Reservation.objects.all().select_related(
        'user', 'room_position__room', 'parking_spot'
    ).order_by('-reservation_date', '-created_at')

    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    user_email = request.GET.get('user')
    status = request.GET.get('status')

    if date_from:
        reservations = reservations.filter(reservation_date__gte=date_from)
    if date_to:
        reservations = reservations.filter(reservation_date__lte=date_to)
    if user_email:
        reservations = reservations.filter(user__email__icontains=user_email)
    if status:
        reservations = reservations.filter(status=status)

    return render(request, 'booking/admin_reservations.html', {
        'reservations': reservations,
    })


@login_required
@user_passes_test(is_admin)
def reservation_export_view(request):
    reservations = Reservation.objects.all().select_related('user', 'room_position__room', 'parking_spot')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    if date_from:
        reservations = reservations.filter(reservation_date__gte=date_from)
    if date_to:
        reservations = reservations.filter(reservation_date__lte=date_to)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="reservas.csv"'
    response.write('\ufeff')

    writer = csv.writer(response)
    writer.writerow(['ID', 'Usuário', 'E-mail', 'Data', 'Período', 'Sala', 'Posição', 'Vaga', 'Status', 'Criada em'])

    for r in reservations:
        writer.writerow([
            r.id, r.user.get_full_name(), r.user.email,
            r.reservation_date, r.get_period_display(),
            r.room_position.room.name, r.room_position.code,
            r.parking_spot.code if r.parking_spot else '',
            r.get_status_display(), r.created_at.strftime('%d/%m/%Y %H:%M'),
        ])

    return response
