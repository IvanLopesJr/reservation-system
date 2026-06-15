from datetime import date

from django import forms

from parking.models import ParkingSpot
from rooms.models import RoomPosition
from .models import Reservation


class ReservationForm(forms.Form):
    reservation_date = forms.DateField(
        label='Data',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )

    def __init__(self, *args, **kwargs):
        min_date = kwargs.pop('min_date', str(date.today()))
        super().__init__(*args, **kwargs)
        self.fields['reservation_date'].widget.attrs['min'] = min_date
    period = forms.ChoiceField(
        label='Período',
        choices=[('', '--- Selecione ---')] + list(Reservation.Period.choices),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    room_position = forms.ModelChoiceField(
        queryset=RoomPosition.objects.all(), label='Posição', required=False,
        widget=forms.HiddenInput()
    )
    wants_parking = forms.BooleanField(
        label='Quero vaga de estacionamento', required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    parking_spot = forms.ModelChoiceField(
        queryset=ParkingSpot.objects.all(), label='Vaga de estacionamento', required=False,
        widget=forms.HiddenInput()
    )


class ReservationCancelForm(forms.Form):
    reason = forms.CharField(
        label='Motivo do cancelamento', required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
