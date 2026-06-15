from django import forms
from .models import Room, RoomPosition


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['name', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'name': 'Nome',
            'description': 'Descrição',
            'is_active': 'Ativo',
        }


class RoomPositionForm(forms.ModelForm):
    class Meta:
        model = RoomPosition
        fields = ['code', 'description', 'status']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'code': 'Código',
            'description': 'Descrição',
            'status': 'Status',
        }
