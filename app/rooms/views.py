from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from .models import Room, RoomPosition
from .forms import RoomForm, RoomPositionForm


def is_admin(user):
    return user.is_authenticated and user.is_staff


@login_required
@user_passes_test(is_admin)
def room_list_view(request):
    rooms = Room.objects.all().order_by('name')
    return render(request, 'rooms/room_list.html', {'rooms': rooms})


@login_required
@user_passes_test(is_admin)
def room_create_view(request):
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sala criada com sucesso.')
            return redirect('rooms:room_list')
    else:
        form = RoomForm()
    return render(request, 'rooms/room_form.html', {'form': form, 'is_create': True})


@login_required
@user_passes_test(is_admin)
def room_update_view(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sala atualizada com sucesso.')
            return redirect('rooms:room_list')
    else:
        form = RoomForm(instance=room)
    return render(request, 'rooms/room_form.html', {'form': form, 'is_create': False, 'room': room})


@login_required
@user_passes_test(is_admin)
def room_toggle_active_view(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    if request.method == 'POST':
        room.is_active = not room.is_active
        room.save()
        messages.success(request, f'Sala {room.name} {"ativada" if room.is_active else "inativada"}.')
    return redirect('rooms:room_list')


@login_required
@user_passes_test(is_admin)
def position_list_view(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    positions = room.positions.all().order_by('code')
    return render(request, 'rooms/position_list.html', {'room': room, 'positions': positions})


@login_required
@user_passes_test(is_admin)
def position_create_view(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    if request.method == 'POST':
        form = RoomPositionForm(request.POST)
        if form.is_valid():
            position = form.save(commit=False)
            position.room = room
            position.save()
            messages.success(request, f'Posição {position.code} criada.')
            return redirect('rooms:position_list', room_id=room.id)
    else:
        form = RoomPositionForm()
    return render(request, 'rooms/position_form.html', {'form': form, 'room': room, 'is_create': True})


@login_required
@user_passes_test(is_admin)
def position_update_view(request, room_id, pk):
    room = get_object_or_404(Room, id=room_id)
    position = get_object_or_404(RoomPosition, id=pk, room=room)
    if request.method == 'POST':
        form = RoomPositionForm(request.POST, instance=position)
        if form.is_valid():
            form.save()
            messages.success(request, f'Posição {position.code} atualizada.')
            return redirect('rooms:position_list', room_id=room.id)
    else:
        form = RoomPositionForm(instance=position)
    return render(request, 'rooms/position_form.html', {'form': form, 'room': room, 'position': position, 'is_create': False})


@login_required
@user_passes_test(is_admin)
def position_toggle_status_view(request, room_id, pk):
    position = get_object_or_404(RoomPosition, id=pk, room_id=room_id)
    if request.method == 'POST':
        if position.status == 'available':
            position.status = 'blocked'
        elif position.status == 'blocked':
            position.status = 'inactive'
        else:
            position.status = 'available'
        position.save()
        messages.success(request, f'Status da posição {position.code} alterado para {position.get_status_display()}.')
    return redirect('rooms:position_list', room_id=room_id)
