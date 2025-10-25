"""
Rental agreement management forms
"""

from django import forms
from .models import RentalAgreement

class RentalAgreementForm(forms.ModelForm):
    """Form for creating/editing rental agreements"""

    class Meta:
        model = RentalAgreement
        fields = [
            'tenant', 'room', 'start_date', 'end_date',
            'rent_amount', 'deposit_amount', 'status',
            'notice_given_date', 'notice_period_days',
            'special_terms', 'security_deposit_returned', 'security_deposit_return_date'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'notice_given_date': forms.DateInput(attrs={'type': 'date'}),
            'security_deposit_return_date': forms.DateInput(attrs={'type': 'date'}),
            'rent_amount': forms.NumberInput(attrs={
                'step': '0.01',
                'min': '0.01'
            }),
            'deposit_amount': forms.NumberInput(attrs={
                'step': '0.01',
                'min': '0'
            }),
            'notice_period_days': forms.NumberInput(attrs={
                'min': '1',
                'max': '365'
            }),
            'special_terms': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Only show tenants without active rental agreements
        from tenants.models import Tenant
        active_agreements = RentalAgreement.objects.filter(
            status__in=['draft', 'active']
        ).values_list('tenant_id', flat=True)
        self.fields['tenant'].queryset = Tenant.objects.exclude(
            id__in=active_agreements
        ).filter(
            tenant_status__in=['prospective', 'active']
        ).order_by('name')

        # Only show rooms without active rental agreements
        from properties.models import Room
        active_room_agreements = RentalAgreement.objects.filter(
            status__in=['draft', 'active']
        ).values_list('room_id', flat=True)
        self.fields['room'].queryset = Room.objects.exclude(
            id__in=active_room_agreements
        ).filter(
            status__in=['available', 'occupied']
        ).order_by('location__name', 'room_number')

        # Set default dates for new agreements
        if not self.instance.pk:
            from datetime import date, timedelta
            today = date.today()
            self.fields['start_date'].initial = today
            self.fields['end_date'].initial = today + timedelta(days=365)  # 1 year default

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        tenant = cleaned_data.get('tenant')
        room = cleaned_data.get('room')

        # Validate dates
        if start_date and end_date and start_date >= end_date:
            raise forms.ValidationError("End date must be after start date")

        # Check for conflicting agreements
        if tenant:
            conflicting_tenant = RentalAgreement.objects.filter(
                tenant=tenant,
                status__in=['draft', 'active'],
                start_date__lte=end_date,
                end_date__gte=start_date
            ).exclude(pk=self.instance.pk if self.instance.pk else None)
            if conflicting_tenant.exists():
                raise forms.ValidationError("Tenant already has an active agreement in this period")

        if room:
            conflicting_room = RentalAgreement.objects.filter(
                room=room,
                status__in=['draft', 'active'],
                start_date__lte=end_date,
                end_date__gte=start_date
            ).exclude(pk=self.instance.pk if self.instance.pk else None)
            if conflicting_room.exists():
                raise forms.ValidationError("Room already has an active agreement in this period")

        return cleaned_data
