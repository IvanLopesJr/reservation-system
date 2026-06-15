from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from booking.models import Reservation
from .models import ParkingSpot
from .forms import ParkingSpotForm


def is_admin(user):
    return user.is_authenticated and user.is_staff


@login_required
@user_passes_test(is_admin)
def parking_spot_list_view(request):
    spots = ParkingSpot.objects.all().order_by('code')
    return render(request, 'parking/parking_spot_list.html', {'spots': spots})


@login_required
@user_passes_test(is_admin)
def parking_spot_create_view(request):
    if request.method == 'POST':
        form = ParkingSpotForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vaga criada com sucesso.')
            return redirect('parking:parking_spot_list')
    else:
        form = ParkingSpotForm()
    return render(request, 'parking/parking_spot_form.html', {'form': form, 'is_create': True})


@login_required
@user_passes_test(is_admin)
def parking_spot_update_view(request, spot_id):
    spot = get_object_or_404(ParkingSpot, id=spot_id)
    if request.method == 'POST':
        form = ParkingSpotForm(request.POST, instance=spot)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vaga atualizada com sucesso.')
            return redirect('parking:parking_spot_list')
    else:
        form = ParkingSpotForm(instance=spot)
    return render(request, 'parking/parking_spot_form.html', {'form': form, 'is_create': False, 'spot': spot})


@login_required
@user_passes_test(is_admin)
def parking_spot_toggle_status_view(request, spot_id):
    spot = get_object_or_404(ParkingSpot, id=spot_id)
    if request.method == 'POST':
        if spot.status == 'available':
            spot.status = 'blocked'
        elif spot.status == 'blocked':
            spot.status = 'inactive'
        else:
            spot.status = 'available'
        spot.save()
        messages.success(request, f'Status da vaga {spot.code} alterado para {spot.get_status_display()}.')
    return redirect('parking:parking_spot_list')


@login_required
@user_passes_test(is_admin)
def parking_spot_delete_view(request, spot_id):
    spot = get_object_or_404(ParkingSpot, id=spot_id)

    if request.method == 'POST':
        active = Reservation.objects.filter(
            parking_spot=spot, status='active'
        ).exists()
        if active:
            messages.error(request, f'Não é possível excluir a vaga "{spot.code}" pois existem reservas ativas.')
            return redirect('parking:parking_spot_list')
        spot.delete()
        messages.success(request, f'Vaga "{spot.code}" excluída permanentemente.')
        return redirect('parking:parking_spot_list')

    return render(request, 'parking/parking_spot_confirm_delete.html', {'spot': spot})
