from django import forms
from .models import Reservation

class ReservationForm(forms.ModelForm):
    class Meta:
        model= Reservation
        fields = ('start_time', 'end_time')
        widgets = {
            'start-time': forms.DateTimeInput(
                format = '%Y-%m-%dT%H:%M',
                attrs = {
                    'class': 'form-control',
                    'type': 'datetime-local' 
                }
            )
        }