# webpage/forms.py

from django import forms
from .models import PlayerProfile

class PlayerProfileForm(forms.ModelForm):
    class Meta:
        model = PlayerProfile
        fields = [
            'profile_picture',
            'game', 'experience', 'state', 'district', 'college',
            'country', 'skills', 'self_rating', 'available_from', 'available_to', 'bio'
        ]
        widgets = {
            'available_from': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
            'available_to': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
            'bio': forms.Textarea(attrs={'rows': 3}),
            'skills': forms.Textarea(attrs={
                'placeholder': 'Enter skills like: mp40, sniper, healer, support',
            }),
        }
