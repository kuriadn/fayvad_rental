"""
Document management forms
File upload and document management
"""

from django import forms
from .models import Document, DocumentType, DocumentStatus

class DocumentForm(forms.ModelForm):
    """Form for creating/editing documents"""

    class Meta:
        model = Document
        fields = [
            'title', 'document_type', 'file', 'description',
            'tenant', 'rental_agreement', 'room',
            'status', 'is_required', 'tags', 'version',
            'is_public', 'reviewed_by'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'tags': forms.TextInput(attrs={
                'placeholder': 'Enter tags separated by commas'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Show all tenants (documents can be associated with any tenant)
        from tenants.models import Tenant
        self.fields['tenant'].queryset = Tenant.objects.all().order_by('name')

        # Filter rental agreements based on selected tenant (if editing existing document)
        from rentals.models import RentalAgreement
        if self.instance.pk and self.instance.tenant:
            self.fields['rental_agreement'].queryset = RentalAgreement.objects.filter(
                tenant=self.instance.tenant
            ).order_by('-start_date')
        else:
            # For new documents, show all agreements
            self.fields['rental_agreement'].queryset = RentalAgreement.objects.all().order_by('-start_date')

        # Show all rooms (documents can be associated with any room)
        from properties.models import Room
        self.fields['room'].queryset = Room.objects.select_related('location').order_by('location__name', 'room_number')

        # Help text for rental agreement
        self.fields['rental_agreement'].help_text = "Selecting a rental agreement will auto-populate tenant and room fields"

    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get('file')
        file_size = cleaned_data.get('file_size')

        # Validate file size if provided
        if file and file.size > 10 * 1024 * 1024:  # 10MB limit
            raise forms.ValidationError("File size cannot exceed 10MB")

        return cleaned_data


class DocumentUpdateForm(forms.ModelForm):
    """Form for updating documents"""

    class Meta:
        model = Document
        fields = [
            'title', 'description', 'status', 'is_required',
            'tags', 'version', 'reviewed_by'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'tags': forms.TextInput(attrs={
                'placeholder': 'Enter tags separated by commas'
            }),
        }


class DocumentUploadForm(forms.ModelForm):
    """Form for uploading documents"""

    class Meta:
        model = Document
        fields = [
            'title', 'document_type', 'file', 'description',
            'tenant', 'rental_agreement', 'room', 'tags'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'tags': forms.TextInput(attrs={
                'placeholder': 'Enter tags separated by commas'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Show all tenants (documents can be associated with any tenant)
        from tenants.models import Tenant
        self.fields['tenant'].queryset = Tenant.objects.all().order_by('name')

        # Show all rental agreements
        from rentals.models import RentalAgreement
        self.fields['rental_agreement'].queryset = RentalAgreement.objects.all().order_by('-start_date')

        # Show all rooms (documents can be associated with any room)
        from properties.models import Room
        self.fields['room'].queryset = Room.objects.select_related('location').order_by('location__name', 'room_number')

        # Help text for rental agreement
        self.fields['rental_agreement'].help_text = "Selecting a rental agreement will auto-populate tenant and room fields"

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.uploaded_by = self.user
        if commit:
            instance.save()
        return instance


class DocumentFilterForm(forms.Form):
    """Form for filtering documents"""

    document_type = forms.ChoiceField(
        choices=[('', 'All Types')] + list(DocumentType.choices),
        required=False
    )
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + list(DocumentStatus.choices),
        required=False
    )
    tenant = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label="All Tenants"
    )
    room = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label="All Rooms"
    )
    is_required = forms.NullBooleanField(
        widget=forms.Select(choices=[
            ('', 'All'),
            ('True', 'Required Only'),
            ('False', 'Optional Only')
        ]),
        required=False
    )
    tags = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Filter by tags'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set up querysets
        from tenants.models import Tenant
        from properties.models import Room

        # Show all tenants for filtering
        self.fields['tenant'].queryset = Tenant.objects.all().order_by('name')

        # Show all rooms for filtering
        self.fields['room'].queryset = Room.objects.select_related('location').order_by('location__name', 'room_number')
