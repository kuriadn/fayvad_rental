"""
Property management views
Locations and Rooms management
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.urls import reverse
from .models import Location, Room, RoomStatus, RoomType
from .forms import LocationForm, RoomForm

@login_required
def location_list(request):
    """List all locations"""
    locations = Location.objects.all().order_by('name')

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        locations = locations.filter(
            Q(name__icontains=search_query) |
            Q(code__icontains=search_query) |
            Q(address__icontains=search_query) |
            Q(city__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(locations, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_title': 'Locations',
        'page_obj': page_obj,
        'search_query': search_query,
        'total_count': locations.count(),
    }
    return render(request, 'properties/location_list.html', context)

@login_required
def location_detail(request, pk):
    """View location details"""
    location = get_object_or_404(Location, pk=pk)

    # Get related rooms
    rooms = location.rooms.all().order_by('room_number')

    room_count = rooms.count()
    occupied_count = rooms.filter(status='occupied').count()
    available_count = rooms.filter(status='available').count()
    maintenance_count = room_count - occupied_count - available_count

    context = {
        'page_title': f'Location: {location.name}',
        'location': location,
        'rooms': rooms,
        'room_count': room_count,
        'occupied_count': occupied_count,
        'available_count': available_count,
        'maintenance_count': maintenance_count,
    }
    return render(request, 'properties/location_detail.html', context)

@login_required
def location_create(request):
    """Create new location"""
    created_location = None
    if request.method == 'POST':
        form = LocationForm(request.POST)
        if form.is_valid():
            created_location = form.save()
            messages.success(request, f'Location "{created_location.name}" created successfully!')
            # Reset form for next entry
            form = LocationForm()
    else:
        form = LocationForm()

    context = {
        'page_title': 'Create Location',
        'form': form,
        'created_location': created_location,
    }
    return render(request, 'properties/location_form.html', context)

@login_required
def location_update(request, pk):
    """Update existing location"""
    location = get_object_or_404(Location, pk=pk)

    if request.method == 'POST':
        form = LocationForm(request.POST, instance=location)
        if form.is_valid():
            location = form.save()
            messages.success(request, f'Location "{location.name}" updated successfully.')
            return redirect('properties:location_detail', pk=location.pk)
    else:
        form = LocationForm(instance=location)

    context = {
        'page_title': f'Edit Location: {location.name}',
        'form': form,
        'location': location,
    }
    return render(request, 'properties/location_form.html', context)

@login_required
def location_delete(request, pk):
    """Delete location"""
    location = get_object_or_404(Location, pk=pk)

    if request.method == 'POST':
        location_name = location.name
        location.delete()
        messages.success(request, f'Location "{location_name}" deleted successfully.')
        return redirect('properties:location_list')

    context = {
        'page_title': f'Delete Location: {location.name}',
        'object': location,
        'object_name': 'location',
        'cancel_url': reverse('properties:location_detail', kwargs={'pk': pk}),
    }
    return render(request, 'properties/location_confirm_delete.html', context)

@login_required
def room_list(request):
    """List all rooms"""
    rooms = Room.objects.select_related('location').order_by('location__name', 'room_number')

    # Filters
    location_filter = request.GET.get('location', '')
    status_filter = request.GET.get('status', '')
    type_filter = request.GET.get('type', '')

    if location_filter:
        rooms = rooms.filter(location_id=location_filter)
    if status_filter:
        rooms = rooms.filter(status=status_filter)
    if type_filter:
        rooms = rooms.filter(room_type=type_filter)

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        rooms = rooms.filter(
            Q(room_number__icontains=search_query) |
            Q(location__name__icontains=search_query) |
            Q(location__code__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(rooms, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get filter options
    locations = Location.objects.filter(is_active=True).order_by('name')
    room_statuses = RoomStatus.choices
    room_types = RoomType.choices

    # Check if user can delete rooms
    can_delete_rooms = request.user.groups.filter(name__in=['Manager', 'Admin']).exists()

    context = {
        'page_title': 'Rooms',
        'page_obj': page_obj,
        'search_query': search_query,
        'location_filter': location_filter,
        'status_filter': status_filter,
        'type_filter': type_filter,
        'locations': locations,
        'room_statuses': room_statuses,
        'room_types': room_types,
        'total_count': rooms.count(),
        'can_delete_rooms': can_delete_rooms,
    }
    return render(request, 'properties/room_list.html', context)

@login_required
def room_detail(request, pk):
    """View room details"""
    room = get_object_or_404(Room.objects.select_related('location'), pk=pk)

    # Check if user can delete rooms
    can_delete_rooms = request.user.groups.filter(name__in=['Manager', 'Admin']).exists()

    context = {
        'page_title': f'Room: {room.full_room_identifier}',
        'room': room,
        'can_delete_rooms': can_delete_rooms,
    }
    return render(request, 'properties/room_detail.html', context)

@login_required
def room_create(request):
    """Create new room"""
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save()
            messages.success(request, f'Room "{room.full_room_identifier}" created successfully.')
            return redirect('properties:room_detail', pk=room.pk)
    else:
        form = RoomForm()

    context = {
        'page_title': 'Create Room',
        'form': form,
    }
    return render(request, 'properties/room_form.html', context)

@login_required
def room_update(request, pk):
    """Update existing room"""
    room = get_object_or_404(Room, pk=pk)

    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            room = form.save()
            messages.success(request, f'Room "{room.full_room_identifier}" updated successfully.')
            return redirect('properties:room_detail', pk=room.pk)
    else:
        form = RoomForm(instance=room)

    context = {
        'page_title': f'Edit Room: {room.full_room_identifier}',
        'form': form,
        'room': room,
    }
    return render(request, 'properties/room_form.html', context)

@login_required
def room_delete(request, pk):
    """
    Delete room - restricted to managers/owners only
    """
    # Check permissions - only managers/owners can delete rooms
    if not request.user.groups.filter(name__in=['Manager', 'Admin']).exists():
        messages.error(request, 'You do not have permission to delete rooms.')
        return redirect('properties:room_detail', pk=pk)

    room = get_object_or_404(Room.objects.select_related('location'), pk=pk)

    # Check if room has active agreements
    active_agreements = room.rental_agreements.filter(status__in=['active', 'draft']).exists()

    if request.method == 'POST':
        # Additional safety checks
        if active_agreements:
            messages.error(request, 'Cannot delete room with active rental agreements.')
            return redirect('properties:room_detail', pk=pk)

        # Log the deletion for audit trail
        room_identifier = room.full_room_identifier
        room.delete()

        messages.success(request, f'Room "{room_identifier}" has been deleted successfully.')
        return redirect('properties:room_list')

    context = {
        'page_title': f'Delete Room: {room.full_room_identifier}',
        'room': room,
        'active_agreements': active_agreements,
        'can_delete': not active_agreements,
    }

    return render(request, 'properties/room_confirm_delete.html', context)

