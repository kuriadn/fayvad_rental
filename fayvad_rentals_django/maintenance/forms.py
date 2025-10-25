"""
Maintenance request management forms
"""

from django import forms
from django.utils.safestring import mark_safe
from .models import MaintenanceRequest


class MultipleFileInput(forms.FileInput):
    """Custom widget for multiple file uploads"""
    allow_multiple_selected = True

class MaintenanceRequestForm(forms.ModelForm):
    """Form for creating/editing maintenance requests"""

    # Add file upload fields
    photos = forms.FileField(
        required=False,
        widget=MultipleFileInput(attrs={'multiple': True}),
        help_text="Upload photos related to the maintenance issue (optional)"
    )
    documents = forms.FileField(
        required=False,
        widget=MultipleFileInput(attrs={'multiple': True}),
        help_text="Upload documents related to the maintenance issue (optional)"
    )

    class Meta:
        model = MaintenanceRequest
        fields = [
            'title', 'description', 'tenant', 'room',
            'priority', 'estimated_cost', 'scheduled_date'
        ]
        widgets = {
            'scheduled_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local'
            }),
            'estimated_cost': forms.NumberInput(attrs={
                'step': '0.01',
                'min': '0'
            }),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Show all tenants (maintenance requests can be for any tenant)
        from tenants.models import Tenant
        self.fields['tenant'].queryset = Tenant.objects.all().order_by('name')

        # Show all rooms (maintenance requests can be for any room)
        from properties.models import Room
        self.fields['room'].queryset = Room.objects.select_related('location').order_by('location__name', 'room_number')

        # Set priority default and make it not required
        if not self.instance.pk:
            self.fields['priority'].initial = 'medium'
        self.fields['priority'].required = False

    def clean(self):
        cleaned_data = super().clean()
        # Allow any tenant/room combination for maintenance requests
        return cleaned_data

    def save(self, commit=True):
        """Override save to handle file uploads"""
        instance = super().save(commit=False)

        # Handle photo uploads
        photo_files = self.files.getlist('photos') if self.files else []
        if photo_files:
            photo_urls = []
            for photo in photo_files:
                # Save file to media directory
                from django.core.files.storage import default_storage
                from django.core.files.base import ContentFile
                import os
                import uuid

                # Generate unique filename
                ext = os.path.splitext(photo.name)[1]
                filename = f"maintenance/photos/{uuid.uuid4()}{ext}"

                # Save file
                file_path = default_storage.save(filename, ContentFile(photo.read()))
                url = default_storage.url(file_path)
                photo_urls.append(url)

            instance.photos = ','.join(photo_urls)

        # Handle document uploads
        document_files = self.files.getlist('documents') if self.files else []
        if document_files:
            document_urls = []
            for document in document_files:
                # Save file to media directory
                from django.core.files.storage import default_storage
                from django.core.files.base import ContentFile
                import os
                import uuid

                # Generate unique filename
                ext = os.path.splitext(document.name)[1]
                filename = f"maintenance/documents/{uuid.uuid4()}{ext}"

                # Save file
                file_path = default_storage.save(filename, ContentFile(document.read()))
                url = default_storage.url(file_path)
                document_urls.append(url)

            instance.documents = ','.join(document_urls)

        if commit:
            instance.save()
        return instance


class MaintenanceRequestUpdateForm(forms.ModelForm):
    """Form for updating maintenance requests"""

    class Meta:
        model = MaintenanceRequest
        fields = [
            'title', 'description', 'priority', 'status',
            'scheduled_date', 'estimated_cost', 'assigned_to'
        ]
        widgets = {
            'scheduled_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local'
            }),
            'estimated_cost': forms.NumberInput(attrs={
                'step': '0.01',
                'min': '0'
            }),
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class MaintenanceCompleteForm(forms.Form):
    """Form for completing maintenance requests"""

    resolution_notes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        required=True,
        help_text="Describe how the maintenance issue was resolved"
    )
    actual_cost = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={'step': '0.01'}),
        help_text="Actual cost incurred for the maintenance"
    )
    resolution_photos = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2}),
        required=False,
        help_text="JSON array of photo URLs (e.g., ['/media/photo1.jpg', '/media/photo2.jpg'])"
    )
    follow_up_required = forms.BooleanField(
        required=False,
        help_text="Check if follow-up is required"
    )


class MaintenanceAssignForm(forms.Form):
    """Form for assigning maintenance requests"""

    assigned_to = forms.CharField(
        max_length=100,
        required=True,
        help_text="Name of technician or staff member"
    )


class MaintenanceScheduleForm(forms.Form):
    """Form for scheduling maintenance"""

    scheduled_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local'
        }),
        required=True,
        help_text="Schedule maintenance for this date and time"
    )

    def clean_scheduled_date(self):
        """Validate that scheduled date is in the future"""
        scheduled_date = self.cleaned_data.get('scheduled_date')
        if scheduled_date:
            from django.utils import timezone
            if scheduled_date <= timezone.now():
                raise forms.ValidationError("Scheduled date must be in the future.")
        return scheduled_date
