"""
Payment management forms
"""

from django import forms
from .models import Payment

class PaymentForm(forms.ModelForm):
    """Form for creating/editing payments"""

    class Meta:
        model = Payment
        fields = [
            'amount', 'payment_method', 'reference_number',
            'rental_agreement', 'tenant', 'room',
            'status', 'payment_date', 'notes', 'description'
        ]
        widgets = {
            'amount': forms.NumberInput(attrs={
                'step': '0.01',
                'min': '0.01'
            }),
            'payment_date': forms.DateInput(attrs={
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'reference_number': forms.TextInput(attrs={
                'placeholder': 'e.g., M-Pesa transaction ID'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Show all tenants (not just active ones - payments can be recorded for any tenant)
        from tenants.models import Tenant
        self.fields['tenant'].queryset = Tenant.objects.all().order_by('name')

        # Filter rental agreements based on selected tenant (if editing existing payment)
        from rentals.models import RentalAgreement
        if self.instance.pk and self.instance.tenant:
            self.fields['rental_agreement'].queryset = RentalAgreement.objects.filter(
                tenant=self.instance.tenant
            ).order_by('-start_date')
        else:
            # For new payments, show all agreements
            self.fields['rental_agreement'].queryset = RentalAgreement.objects.all().order_by('-start_date')

        # Show all rooms (not just occupied ones - payments can be for any room)
        from properties.models import Room
        self.fields['room'].queryset = Room.objects.select_related('location').order_by('location__name', 'room_number')

        # Set defaults for new payments
        if not self.instance.pk:
            from datetime import date
            self.fields['payment_date'].initial = date.today()
            self.fields['status'].initial = 'pending'

        # Status field has a default so make it optional
        self.fields['status'].required = False

        # Reference number is especially important for mobile payments
        self.fields['reference_number'].help_text = "Required for mobile payments (M-Pesa transaction ID)"

        # Help text for rental agreement
        self.fields['rental_agreement'].help_text = "Selecting a rental agreement will auto-populate tenant and room fields"

    def clean(self):
        cleaned_data = super().clean()
        tenant = cleaned_data.get('tenant')
        rental_agreement = cleaned_data.get('rental_agreement')
        room = cleaned_data.get('room')
        payment_method = cleaned_data.get('payment_method')
        reference_number = cleaned_data.get('reference_number')

        # At least one relationship should be specified
        if not tenant and not rental_agreement and not room:
            raise forms.ValidationError(
                "Please specify at least one: tenant, rental agreement, or room."
            )

        # Reference number is required for mobile payments
        if payment_method == 'mpesa' and not reference_number:
            raise forms.ValidationError(
                "Reference number (M-Pesa transaction ID) is required for mobile payments."
            )

        return cleaned_data


class PaymentUpdateForm(forms.ModelForm):
    """Form for updating payments (includes status field)"""

    class Meta:
        model = Payment
        fields = [
            'amount', 'payment_method', 'reference_number',
            'rental_agreement', 'tenant', 'room',
            'status', 'payment_date', 'notes', 'description'
        ]
        widgets = {
            'amount': forms.NumberInput(attrs={
                'step': '0.01',
                'min': '0.01'
            }),
            'payment_date': forms.DateInput(attrs={
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'reference_number': forms.TextInput(attrs={
                'placeholder': 'e.g., M-Pesa transaction ID'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Show all tenants
        from tenants.models import Tenant
        self.fields['tenant'].queryset = Tenant.objects.all().order_by('name')

        # Filter rental agreements based on selected tenant
        from rentals.models import RentalAgreement
        if self.instance.pk and self.instance.tenant:
            self.fields['rental_agreement'].queryset = RentalAgreement.objects.filter(
                tenant=self.instance.tenant
            ).order_by('-start_date')
        else:
            self.fields['rental_agreement'].queryset = RentalAgreement.objects.all().order_by('-start_date')

        # Show all rooms
        from properties.models import Room
        self.fields['room'].queryset = Room.objects.select_related('location').order_by('location__name', 'room_number')

        # Help text for rental agreement
        self.fields['rental_agreement'].help_text = "Selecting a rental agreement will auto-populate tenant and room fields"


class TenantPaymentReportForm(forms.ModelForm):
    """Form for tenants to report payments - simplified version"""

    class Meta:
        model = Payment
        fields = [
            'amount', 'payment_method', 'reference_number',
            'payment_date', 'notes'
        ]
        widgets = {
            'amount': forms.NumberInput(attrs={
                'step': '0.01',
                'min': '0.01',
                'placeholder': 'Enter payment amount'
            }),
            'payment_date': forms.DateInput(attrs={
                'type': 'date'
            }),
            'reference_number': forms.TextInput(attrs={
                'placeholder': 'M-Pesa transaction ID or receipt number'
            }),
            'notes': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Any additional notes about this payment'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)

        # Set tenant-specific defaults
        if self.tenant:
            # Auto-populate tenant and related fields
            self.instance.tenant = self.tenant
            self.instance.room = self.tenant.current_room
            self.instance.rental_agreement = getattr(self.tenant, 'rental_agreement', None)
            self.instance.status = 'pending'
            self.instance.created_by = getattr(self.tenant, 'user', None)

        # Set default payment date to today
        if not self.instance.pk:
            from datetime import date
            self.fields['payment_date'].initial = date.today()

        # Make reference number required for mobile payments
        self.fields['reference_number'].help_text = "Required for mobile payments (M-Pesa transaction ID)"

    def clean(self):
        cleaned_data = super().clean()
        payment_method = cleaned_data.get('payment_method')
        reference_number = cleaned_data.get('reference_number')

        # Reference number is required for mobile payments
        if payment_method == 'mpesa' and not reference_number:
            raise forms.ValidationError(
                "Reference number (M-Pesa transaction ID) is required for mobile payments."
            )

        return cleaned_data
