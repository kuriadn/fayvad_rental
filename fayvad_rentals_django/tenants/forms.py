"""
Tenant forms for Django
Preserves all functionality from FastAPI tenant management
"""

from django import forms
from django.contrib.auth.models import User
from .models import Tenant, TenantStatus, ComplianceStatus, TenantType, Complaint, ComplaintStatus, ComplaintPriority, ComplaintCategory

class TenantForm(forms.ModelForm):
    """Form for creating and updating tenants"""

    class Meta:
        model = Tenant
        fields = [
            'name', 'email', 'phone', 'id_number',
            'emergency_contact_name', 'emergency_contact_phone',
            'tenant_type', 'institution_employer',
            'tenant_status', 'compliance_status', 'compliance_notes',
            'account_balance', 'user'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Enter full name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Enter email address'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Enter phone number'
            }),
            'id_number': forms.TextInput(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Enter ID number'
            }),
            'emergency_contact_name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Enter emergency contact name'
            }),
            'emergency_contact_phone': forms.TextInput(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Enter emergency contact phone'
            }),
            'institution_employer': forms.TextInput(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Enter institution or employer'
            }),
            'compliance_notes': forms.Textarea(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500',
                'rows': 3,
                'placeholder': 'Enter compliance notes'
            }),
            'account_balance': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500',
                'step': '0.01'
            }),
            'tenant_status': forms.Select(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500'
            }),
            'compliance_status': forms.Select(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500'
            }),
            'tenant_type': forms.Select(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500'
            }),
            'user': forms.Select(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500'
            }),
        }

    def clean_email(self):
        """Validate email uniqueness"""
        email = self.cleaned_data.get('email')
        if email:
            # Check if email is already used by another tenant
            queryset = Tenant.objects.filter(email=email)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise forms.ValidationError("This email is already registered to another tenant.")
        return email

    def clean_id_number(self):
        """Validate ID number uniqueness"""
        id_number = self.cleaned_data.get('id_number')
        if id_number:
            # Check if ID number is already used by another tenant
            queryset = Tenant.objects.filter(id_number=id_number)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise forms.ValidationError("This ID number is already registered to another tenant.")
        return id_number

class TenantSearchForm(forms.Form):
    """Form for searching and filtering tenants"""

    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name, email, or phone...'
        })
    )

    tenant_status = forms.ChoiceField(
        required=False,
        choices=[('', 'All Statuses')] + list(TenantStatus.choices),
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    tenant_type = forms.ChoiceField(
        required=False,
        choices=[('', 'All Types')] + list(TenantType.choices),
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    compliance_status = forms.ChoiceField(
        required=False,
        choices=[('', 'All Compliance')] + list(ComplianceStatus.choices),
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

class TenantOnboardingForm(forms.ModelForm):
    """
    Specialized form for tenant onboarding
    Includes all required fields for new tenant registration
    """

    class Meta:
        model = Tenant
        fields = [
            'name', 'email', 'phone', 'id_number',
            'emergency_contact_name', 'emergency_contact_phone',
            'tenant_type', 'institution_employer'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'required': True
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True
            }),
            'id_number': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True
            }),
            'emergency_contact_name': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True
            }),
            'emergency_contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True
            }),
            'tenant_type': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'institution_employer': forms.TextInput(attrs={
                'class': 'form-control'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default status for onboarding
        if not self.instance.pk:
            self.instance.tenant_status = TenantStatus.PROSPECTIVE
            self.instance.compliance_status = ComplianceStatus.COMPLIANT


class TenantComplaintForm(forms.ModelForm):
    """Form for tenant complaint submission - only shows rooms they occupy"""

    # Explicitly define room field with proper queryset
    room = forms.ModelChoiceField(
        queryset=None,  # Will be set in __init__
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text='Select the room where you are experiencing the issue'
    )

    class Meta:
        model = Complaint
        fields = [
            'category', 'priority', 'subject', 'description',
            'room', 'is_anonymous', 'contact_preference'
        ]
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Brief summary of your complaint',
                'maxlength': 200
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Please provide detailed information about your complaint...',
                'rows': 6
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'contact_preference': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Set up room queryset based on tenant's agreements
        from properties.models import Room
        base_queryset = Room.objects.select_related('location').order_by('location__name', 'room_number')

        if self.user:
            try:
                tenant_profile = self.user.tenant_profile
                # Get rooms from tenant's active or draft agreements
                from rentals.models import RentalAgreement
                active_rooms = RentalAgreement.objects.filter(
                    tenant=tenant_profile,
                    status__in=['active', 'draft']
                ).values_list('room', flat=True)

                if active_rooms:
                    self.fields['room'].queryset = base_queryset.filter(id__in=active_rooms)
                else:
                    # No active agreements, no rooms
                    self.fields['room'].queryset = base_queryset.none()
            except:
                # No tenant profile, no rooms
                self.fields['room'].queryset = base_queryset.none()
        else:
            # No user, no rooms
            self.fields['room'].queryset = base_queryset.none()

        # Make contact_preference not required since it has a default
        self.fields['contact_preference'].required = False

        # Make room optional
        self.fields['room'].required = False
        self.fields['priority'].initial = 'medium'


class ComplaintForm(forms.ModelForm):
    """Form for staff complaint submission - shows all rooms"""

    # Explicitly define room field for staff
    room = forms.ModelChoiceField(
        queryset=None,  # Will be set in __init__
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text='Select the room related to this complaint'
    )

    class Meta:
        model = Complaint
        fields = [
            'tenant', 'category', 'priority', 'subject', 'description',
            'room', 'is_anonymous', 'contact_preference'
        ]
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Brief summary of your complaint',
                'maxlength': 200
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Please provide detailed information about your complaint...',
                'rows': 6
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'tenant': forms.Select(attrs={'class': 'form-select'}),
            'contact_preference': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Staff form shows all rooms and tenants
        from properties.models import Room
        self.fields['room'].queryset = Room.objects.select_related('location').order_by('location__name', 'room_number')

        # Make contact_preference not required since it has a default
        self.fields['contact_preference'].required = False

        # Make room optional
        self.fields['room'].required = False
        self.fields['priority'].initial = 'medium'


class ComplaintUpdateForm(forms.ModelForm):
    """Form for staff to update complaint details"""

    class Meta:
        model = Complaint
        fields = [
            'assigned_to', 'priority', 'status', 'resolution'
        ]
        widgets = {
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'resolution': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Resolution details and actions taken...',
                'rows': 4
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from accounts.models import Staff
        self.fields['assigned_to'].queryset = Staff.objects.filter(is_active_staff=True)


class ComplaintSearchForm(forms.Form):
    """Form for filtering complaints"""

    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Search complaints...'
        })
    )

    status = forms.ChoiceField(
        required=False,
        choices=[('', 'All Status')] + list(ComplaintStatus.choices),
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    priority = forms.ChoiceField(
        required=False,
        choices=[('', 'All Priorities')] + list(ComplaintPriority.choices),
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    category = forms.ChoiceField(
        required=False,
        choices=[('', 'All Categories')] + list(ComplaintCategory.choices),
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    assigned_to = forms.ModelChoiceField(
        required=False,
        queryset=None,
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="All Staff"
    )

    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-input',
            'type': 'date'
        })
    )

    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-input',
            'type': 'date'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from accounts.models import Staff
        self.fields['assigned_to'].queryset = Staff.objects.filter(is_active_staff=True)
