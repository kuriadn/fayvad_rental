"""
Property management forms
"""

from django import forms
from .models import Location, Room

class LocationForm(forms.ModelForm):
    """Form for creating/editing locations"""

    class Meta:
        model = Location
        fields = [
            'name', 'code', 'address', 'city',
            'manager', 'is_active'
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'code': forms.TextInput(attrs={
                'placeholder': 'e.g., BLDA, CAMPUS',
                'style': 'text-transform: uppercase;'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active staff members who can manage locations
        from accounts.models import Staff
        self.fields['manager'].queryset = Staff.objects.filter(
            is_active_staff=True,
            role__in=['manager', 'caretaker']
        ).order_by('user__full_name').select_related('user')

    def clean_code(self):
        """Ensure code is uppercase"""
        code = self.cleaned_data.get('code', '')
        return code.upper() if code else code

class RoomForm(forms.ModelForm):
    """Form for creating/editing rooms"""

    class Meta:
        model = Room
        fields = [
            'location', 'room_number', 'room_type', 'floor', 'capacity',
            'status', 'description'
        ]
        widgets = {
            'capacity': forms.NumberInput(attrs={
                'min': '1',
                'max': '10'
            }),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active locations
        self.fields['location'].queryset = Location.objects.filter(is_active=True).order_by('name')

