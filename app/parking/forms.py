from django import forms
from .models import ParkingSpot


class ParkingSpotForm(forms.ModelForm):
    class Meta:
        model = ParkingSpot
        fields = ['code', 'type', 'description', 'status']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'code': 'Código',
            'type': 'Tipo',
            'description': 'Descrição',
            'status': 'Status',
        }
