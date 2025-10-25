"""
Accounts views
User profile and account management
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.core.exceptions import ValidationError
from .forms import ProfileForm, TenantLoginForm, StaffForm, UserStaffForm
from .models import User, Staff

@login_required
def profile(request):
    """User profile view"""
    return render(request, 'accounts/profile.html', {
        'page_title': 'My Profile',
        'user': request.user,
    })

@login_required
def profile_edit(request):
    """Edit user profile"""
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        password_form = PasswordChangeForm(request.user, request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('accounts:profile')

        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)  # Keep user logged in
            messages.success(request, 'Password changed successfully.')
            return redirect('accounts:profile')

    else:
        form = ProfileForm(instance=request.user)
        password_form = PasswordChangeForm(request.user)

    return render(request, 'accounts/profile_edit.html', {
        'form': form,
        'password_form': password_form,
        'page_title': 'Edit Profile',
    })

def tenant_login(request):
    """Tenant login view using phone and ID number"""
    if request.user.is_authenticated:
        # If user is already logged in, redirect based on their role
        try:
            # Check if user has a tenant profile
            tenant_profile = request.user.tenant_profile
            return redirect('tenants:tenant_dashboard', tenant_id=tenant_profile.id)
        except:
            # User doesn't have tenant profile, redirect to staff dashboard
            return redirect('dashboard:dashboard_overview')

    if request.method == 'POST':
        form = TenantLoginForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone']
            id_number = form.cleaned_data['id_number']

            # Try to find tenant by phone and ID number
            try:
                from tenants.models import Tenant
                tenant = Tenant.objects.select_related('user').get(
                    phone=phone,
                    id_number=id_number,
                    tenant_status__in=['active', 'prospective']
                )

                if tenant.user and tenant.user.is_active:
                    # Log in the associated user
                    login(request, tenant.user)
                    messages.success(request, f'Welcome back, {tenant.name}!')
                    return redirect('tenants:tenant_dashboard', tenant_id=tenant.id)
                else:
                    messages.error(request, 'Your account is not active. Please contact support.')

            except Tenant.DoesNotExist:
                messages.error(request, 'Invalid phone number or ID number. Please check your details and try again.')
            except Exception as e:
                messages.error(request, 'Login failed. Please try again.')
    else:
        form = TenantLoginForm()

    return render(request, 'accounts/login_tenant.html', {
        'form': form,
        'page_title': 'Tenant Login',
    })


def superuser_required(view_func):
    """Decorator to require superuser access"""
    return user_passes_test(lambda u: u.is_superuser)(view_func)


@superuser_required
def user_list(request):
    """List all users with optional staff designation - Superuser only"""
    users = User.objects.all().order_by('username')

    # Calculate user statistics
    from django.db.models import Count, Q
    user_stats = {
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'staff_users': User.objects.filter(~Q(staff_profile=None)).count(),
        'superusers': User.objects.filter(is_superuser=True).count(),
    }

    # Get staff statistics by role
    staff_stats = Staff.objects.values('role').annotate(
        count=Count('id')
    ).order_by('role')

    return render(request, 'accounts/user_list.html', {
        'users': users,
        'user_stats': user_stats,
        'staff_stats': staff_stats,
        'page_title': 'User Management',
    })


@superuser_required
def user_create(request):
    """Create new user with optional staff designation - Superuser only"""
    if request.method == 'POST':
        form = UserStaffForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'User {user.username} created successfully.')
            return redirect('accounts:user_list')
    else:
        form = UserStaffForm()

    return render(request, 'accounts/user_form.html', {
        'form': form,
        'page_title': 'Create User',
        'is_create': True,
    })


@superuser_required
def user_edit(request, pk):
    """Edit user with optional staff designation - Superuser only"""
    user = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        form = UserStaffForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'User {user.username} updated successfully.')
            return redirect('accounts:user_list')
    else:
        form = UserStaffForm(instance=user)

    return render(request, 'accounts/user_form.html', {
        'form': form,
        'user': user,
        'page_title': f'Edit {user.username}',
        'is_create': False,
    })


@superuser_required
def user_delete(request, pk):
    """Delete user - Superuser only"""
    user = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'User {username} deleted successfully.')
        return redirect('accounts:user_list')

    return render(request, 'accounts/user_confirm_delete.html', {
        'user': user,
        'page_title': f'Delete {user.username}',
    })


@superuser_required
def staff_list(request):
    """List all staff members - Superuser only"""
    staff_members = Staff.objects.select_related('user').order_by('user__full_name')

    # Calculate staff statistics by role
    from django.db.models import Count
    staff_stats = Staff.objects.values('role').annotate(
        count=Count('id')
    ).order_by('role')

    return render(request, 'accounts/staff_list.html', {
        'staff_members': staff_members,
        'staff_stats': staff_stats,
        'page_title': 'Staff Management',
    })


@superuser_required
def staff_edit(request, pk):
    """Edit staff member - Superuser only"""
    staff = Staff.objects.select_related('user').get(pk=pk)

    if request.method == 'POST':
        form = StaffForm(request.POST, instance=staff)
        if form.is_valid():
            form.save()
            messages.success(request, f'Staff member {staff.full_name} updated successfully.')
            return redirect('accounts:staff_list')
    else:
        form = StaffForm(instance=staff)

    return render(request, 'accounts/staff_form.html', {
        'form': form,
        'staff': staff,
        'page_title': f'Edit {staff.full_name}',
        'is_create': False,
    })


@superuser_required
def staff_delete(request, pk):
    """Delete staff member - Superuser only"""
    staff = Staff.objects.select_related('user').get(pk=pk)

    if request.method == 'POST':
        user_name = staff.full_name
        # Delete the user account too (cascades to staff profile)
        staff.user.delete()
        messages.success(request, f'Staff member {user_name} deleted successfully.')
        return redirect('accounts:staff_list')

    return render(request, 'accounts/staff_confirm_delete.html', {
        'staff': staff,
        'page_title': f'Delete {staff.full_name}',
    })