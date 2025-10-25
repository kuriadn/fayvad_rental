"""
Accounts forms
User profile forms
"""

from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.core.exceptions import ValidationError
from .models import User, Staff

class ProfileForm(forms.ModelForm):
    """Form for editing user profile"""

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email',
            'phone', 'username'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter last name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter email'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter phone number'
            }),
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter username'
            }),
        }

class UserRegistrationForm(UserCreationForm):
    """Form for user registration"""

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Choose a username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter email address'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter last name'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter phone number'
            }),
        }

class TenantLoginForm(forms.Form):
    """Form for tenant login using phone and ID number"""

    phone = forms.CharField(
        max_length=20,
        label="Phone Number",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '0712345678',
            'type': 'tel'
        }),
        help_text="Enter your phone number in Kenyan format (e.g., 0712345678)"
    )

    id_number = forms.CharField(
        max_length=20,
        label="ID Number",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your ID number'
        }),
        help_text="Enter your national ID number"
    )

    def clean_phone(self):
        """Validate Kenyan phone number format"""
        phone = self.cleaned_data['phone']
        # Remove any spaces or special characters
        phone = ''.join(filter(str.isdigit, phone))

        # Check if it's a valid Kenyan number
        if len(phone) == 9 and phone.startswith(('1', '2', '3', '4', '5', '6', '7', '8', '9')):
            phone = '0' + phone  # Add leading 0 for 10-digit format
        elif len(phone) == 10 and phone.startswith('0'):
            pass  # Already in correct format
        elif len(phone) == 12 and phone.startswith('254'):
            phone = '0' + phone[3:]  # Convert international to local format
        else:
            raise ValidationError('Please enter a valid Kenyan phone number.')

        return phone

    def clean_id_number(self):
        """Validate ID number format"""
        id_number = self.cleaned_data['id_number']
        if len(id_number) < 6 or len(id_number) > 20:
            raise ValidationError('ID number must be between 6 and 20 characters.')
        return id_number


class StaffForm(forms.ModelForm):
    """Form for creating/editing staff members"""

    class Meta:
        model = Staff
        fields = [
            'user', 'role', 'employee_id', 'department',
            'hire_date', 'is_active_staff',
            'emergency_contact_name', 'emergency_contact_phone'
        ]
        widgets = {
            'hire_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show users without existing staff profiles
        if not self.instance.pk:
            existing_staff_users = Staff.objects.values_list('user_id', flat=True)
            self.fields['user'].queryset = User.objects.exclude(
                id__in=existing_staff_users
            ).order_by('username')
        else:
            # For editing, don't allow changing user
            self.fields['user'].disabled = True

    def clean_employee_id(self):
        """Ensure employee ID is unique"""
        employee_id = self.cleaned_data.get('employee_id')
        if employee_id:
            queryset = Staff.objects.filter(employee_id=employee_id)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise ValidationError('Employee ID must be unique.')
        return employee_id


class UserStaffForm(forms.ModelForm):
    """Unified form for creating/editing users with optional staff role"""

    # Password fields (only for new users)
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        help_text="Leave blank to keep existing password (for editing) or set a new password."
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        help_text="Enter the same password as above, for verification."
    )

    # Staff designation
    is_staff_member = forms.BooleanField(
        required=False,
        label="Designate as Staff Member",
        help_text="Check this to assign a staff role to this user"
    )

    # Staff fields (shown conditionally)
    role = forms.ChoiceField(
        choices=Staff.StaffRole.choices,
        required=False,
        help_text="Staff role/position"
    )
    employee_id = forms.CharField(
        max_length=20,
        required=False,
        help_text="Unique employee identification number"
    )
    department = forms.CharField(
        max_length=100,
        required=False,
        help_text="Department or section"
    )
    hire_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text="Date staff member was hired"
    )
    emergency_contact_name = forms.CharField(
        max_length=255,
        required=False,
        help_text="Emergency contact name"
    )
    emergency_contact_phone = forms.CharField(
        max_length=20,
        required=False,
        help_text="Emergency contact phone number"
    )

    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name', 'phone',
            'is_active', 'is_staff', 'is_superuser'
        ]
        help_texts = {
            'is_staff': 'Designates whether the user can log into staff interface.',
            'is_superuser': 'Designates that this user has all permissions without explicitly assigning them.',
            'is_active': 'Designates whether this user should be treated as active.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Handle password fields based on whether this is a new user or existing
        if self.instance and self.instance.pk:
            # Existing user - password fields are optional
            self.fields['password1'].required = False
            self.fields['password2'].required = False
            self.fields['password1'].help_text = "Leave blank to keep current password."
            self.fields['password2'].help_text = "Leave blank to keep current password."
        else:
            # New user - password fields are required
            self.fields['password1'].required = True
            self.fields['password2'].required = True
            self.fields['password1'].help_text = "Enter a password for the new user."
            self.fields['password2'].help_text = "Confirm the password."

        # If editing existing user, check if they have staff profile
        if self.instance and self.instance.pk:
            try:
                staff_profile = self.instance.staff_profile
                self.fields['is_staff_member'].initial = True
                self.fields['role'].initial = staff_profile.role
                self.fields['employee_id'].initial = staff_profile.employee_id
                self.fields['department'].initial = staff_profile.department
                self.fields['hire_date'].initial = staff_profile.hire_date
                self.fields['emergency_contact_name'].initial = staff_profile.emergency_contact_name
                self.fields['emergency_contact_phone'].initial = staff_profile.emergency_contact_phone
            except Staff.DoesNotExist:
                self.fields['is_staff_member'].initial = False

        # Set widget attributes
        for field_name, field in self.fields.items():
            if hasattr(field.widget, 'attrs') and 'class' not in field.widget.attrs and field_name not in ['password1', 'password2']:
                field.widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        # Validate passwords
        if self.instance and self.instance.pk:
            # Existing user - only validate if passwords are provided
            if password1 or password2:
                if password1 != password2:
                    raise forms.ValidationError('Passwords do not match.')
                if len(password1) < 8:
                    raise forms.ValidationError('Password must be at least 8 characters long.')
        else:
            # New user - passwords are required
            if not password1:
                raise forms.ValidationError('Password is required for new users.')
            if not password2:
                raise forms.ValidationError('Password confirmation is required.')
            if password1 != password2:
                raise forms.ValidationError('Passwords do not match.')
            if len(password1) < 8:
                raise forms.ValidationError('Password must be at least 8 characters long.')

        is_staff_member = cleaned_data.get('is_staff_member')

        if is_staff_member:
            # Validate required staff fields
            role = cleaned_data.get('role')
            if not role:
                raise forms.ValidationError('Role is required for staff members.')

            employee_id = cleaned_data.get('employee_id')
            if employee_id:
                # Check uniqueness for new staff or when changing employee_id
                queryset = Staff.objects.filter(employee_id=employee_id)
                if self.instance and self.instance.pk:
                    # For existing users, exclude their current staff profile
                    try:
                        queryset = queryset.exclude(user=self.instance)
                    except Staff.DoesNotExist:
                        pass
                if queryset.exists():
                    raise forms.ValidationError('Employee ID must be unique.')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=commit)

        # Handle password setting
        password1 = self.cleaned_data.get('password1')
        if password1:
            user.set_password(password1)
            if commit:
                user.save()

        is_staff_member = self.cleaned_data.get('is_staff_member')

        if is_staff_member:
            # Create or update staff profile
            staff_data = {
                'role': self.cleaned_data['role'],
                'employee_id': self.cleaned_data.get('employee_id'),
                'department': self.cleaned_data.get('department'),
                'hire_date': self.cleaned_data.get('hire_date'),
                'emergency_contact_name': self.cleaned_data.get('emergency_contact_name'),
                'emergency_contact_phone': self.cleaned_data.get('emergency_contact_phone'),
            }

            staff, created = Staff.objects.get_or_create(
                user=user,
                defaults=staff_data
            )

            if not created:
                # Update existing staff profile
                for key, value in staff_data.items():
                    setattr(staff, key, value)
                staff.save()

        else:
            # Remove staff profile if it exists and user is no longer staff
            try:
                user.staff_profile.delete()
            except Staff.DoesNotExist:
                pass

        return user


