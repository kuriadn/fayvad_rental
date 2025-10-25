"""
Property Service - Pure Django Implementation
Manages locations and rooms with direct Django ORM
"""

from typing import Dict, List, Optional, Any
from django.db.models import Q, Count
from django.core.paginator import Paginator
from properties.models import Location, Room, RoomStatus
import logging

logger = logging.getLogger(__name__)


class PropertyService:
    """
    Pure Django service for property management (locations and rooms)
    """

    # ===== LOCATION OPERATIONS =====

    @staticmethod
    def get_locations(filters: Optional[Dict[str, Any]] = None, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """
        Get list of locations with filtering
        """
        try:
            queryset = Location.objects.select_related('manager').all()

            # Apply filters
            if filters:
                search = filters.get('search')
                if search:
                    queryset = queryset.filter(
                        Q(name__icontains=search) |
                        Q(code__icontains=search) |
                        Q(city__icontains=search)
                    )

                is_active = filters.get('is_active')
                if is_active is not None:
                    queryset = queryset.filter(is_active=is_active)

            # Paginate
            paginator = Paginator(queryset, page_size)
            page_obj = paginator.get_page(page)

            # Serialize
            location_data = [
                {
                    'id': str(location.id),
                    'name': location.name,
                    'code': location.code,
                    'address': location.address,
                    'city': location.city,
                    'is_active': location.is_active,
                    'setup_complete': location.setup_complete,
                    'manager': {
                        'id': location.manager.id,
                        'name': f'{location.manager.first_name} {location.manager.last_name}'
                    } if location.manager else None,
                    'room_count': location.room_count,
                    'occupied_count': location.occupied_room_count,
                    'occupancy_rate': location.occupancy_rate,
                    'monthly_revenue': location.monthly_revenue,
                }
                for location in page_obj
            ]

            return {
                'success': True,
                'data': location_data,
                'total': paginator.count,
                'page': page,
                'pages': paginator.num_pages,
            }

        except Exception as e:
            logger.error(f"Error getting locations: {e}")
            return {
                'success': False,
                'error': str(e),
                'data': []
            }

    @staticmethod
    def get_location(location_id: str) -> Dict[str, Any]:
        """
        Get single location by ID
        """
        try:
            location = Location.objects.select_related('manager').get(id=location_id)

            location_data = {
                'id': str(location.id),
                'name': location.name,
                'code': location.code,
                'address': location.address,
                'city': location.city,
                'is_active': location.is_active,
                'setup_complete': location.setup_complete,
                'setup_date': location.setup_date.isoformat() if location.setup_date else None,
                'manager': {
                    'id': location.manager.id,
                    'name': f'{location.manager.first_name} {location.manager.last_name}'
                } if location.manager else None,
                'room_count': location.room_count,
                'occupied_count': location.occupied_room_count,
                'available_count': location.available_room_count,
                'occupancy_rate': location.occupancy_rate,
                'tenant_count': location.tenant_count,
                'monthly_revenue': location.monthly_revenue,
                'created_at': location.created_at.isoformat(),
                'updated_at': location.updated_at.isoformat(),
            }

            return {
                'success': True,
                'data': location_data
            }

        except Location.DoesNotExist:
            return {
                'success': False,
                'error': 'Location not found'
            }
        except Exception as e:
            logger.error(f"Error getting location {location_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def create_location(location_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create new location
        """
        try:
            from accounts.models import User

            manager_id = location_data.get('manager_id')
            manager = User.objects.get(id=manager_id) if manager_id else None

            location = Location.objects.create(
                name=location_data['name'],
                code=location_data['code'].upper(),
                address=location_data.get('address'),
                city=location_data.get('city'),
                manager=manager,
                is_active=location_data.get('is_active', True),
            )

            return {
                'success': True,
                'data': {
                    'id': str(location.id),
                    'name': location.name,
                    'code': location.code,
                    'created_at': location.created_at.isoformat(),
                },
                'message': 'Location created successfully'
            }

        except Exception as e:
            logger.error(f"Error creating location: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    # ===== ROOM OPERATIONS =====

    @staticmethod
    def get_rooms(filters: Optional[Dict[str, Any]] = None, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """
        Get list of rooms with filtering
        """
        try:
            queryset = Room.objects.select_related('location').all()

            # Apply filters
            if filters:
                search = filters.get('search')
                if search:
                    queryset = queryset.filter(
                        Q(room_number__icontains=search) |
                        Q(location__name__icontains=search)
                    )

                location_id = filters.get('location_id')
                if location_id:
                    queryset = queryset.filter(location_id=location_id)

                status = filters.get('status')
                if status:
                    queryset = queryset.filter(status=status)

                room_type = filters.get('room_type')
                if room_type:
                    queryset = queryset.filter(room_type=room_type)

            # Paginate
            paginator = Paginator(queryset, page_size)
            page_obj = paginator.get_page(page)

            # Serialize
            room_data = [
                {
                    'id': str(room.id),
                    'room_number': room.room_number,
                    'room_type': room.room_type,
                    'status': room.status,
                    'floor': room.floor,
                    'capacity': room.capacity,
                    'location': {
                        'id': str(room.location.id),
                        'name': room.location.name,
                        'code': room.location.code
                    },
                    'full_identifier': room.full_room_identifier,
                    'is_available': room.is_available,
                    'monthly_revenue': room.monthly_revenue,
                }
                for room in page_obj
            ]

            return {
                'success': True,
                'data': room_data,
                'total': paginator.count,
                'page': page,
                'pages': paginator.num_pages,
            }

        except Exception as e:
            logger.error(f"Error getting rooms: {e}")
            return {
                'success': False,
                'error': str(e),
                'data': []
            }

    @staticmethod
    def get_room(room_id: str) -> Dict[str, Any]:
        """
        Get single room by ID
        """
        try:
            room = Room.objects.select_related('location').get(id=room_id)

            # Get current tenant if occupied
            from rentals.models import RentalAgreement
            active_agreement = RentalAgreement.objects.filter(
                room=room,
                status='active'
            ).select_related('tenant').first()

            room_data = {
                'id': str(room.id),
                'room_number': room.room_number,
                'room_type': room.room_type,
                'status': room.status,
                'floor': room.floor,
                'capacity': room.capacity,
                'description': room.description,
                'location': {
                    'id': str(room.location.id),
                    'name': room.location.name,
                    'code': room.location.code
                },
                'full_identifier': room.full_room_identifier,
                'is_available': room.is_available,
                'is_occupied': room.is_occupied,
                'is_under_maintenance': room.is_under_maintenance,
                'monthly_revenue': room.monthly_revenue,
                'current_tenant': {
                    'id': str(active_agreement.tenant.id),
                    'name': active_agreement.tenant.name
                } if active_agreement else None,
                'created_at': room.created_at.isoformat(),
                'updated_at': room.updated_at.isoformat(),
            }

            return {
                'success': True,
                'data': room_data
            }

        except Room.DoesNotExist:
            return {
                'success': False,
                'error': 'Room not found'
            }
        except Exception as e:
            logger.error(f"Error getting room {room_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def create_room(room_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create new room
        """
        try:
            location = Location.objects.get(id=room_data['location_id'])

            room = Room.objects.create(
                room_number=room_data['room_number'],
                room_type=room_data.get('room_type', 'single'),
                location=location,
                floor=room_data.get('floor'),
                capacity=room_data.get('capacity', 1),
                status=room_data.get('status', 'available'),
                description=room_data.get('description'),
            )

            return {
                'success': True,
                'data': {
                    'id': str(room.id),
                    'room_number': room.room_number,
                    'location': location.name,
                    'created_at': room.created_at.isoformat(),
                },
                'message': 'Room created successfully'
            }

        except Location.DoesNotExist:
            return {
                'success': False,
                'error': 'Location not found'
            }
        except Exception as e:
            logger.error(f"Error creating room: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def update_room_status(room_id: str, new_status: str) -> Dict[str, Any]:
        """
        Update room status
        """
        try:
            room = Room.objects.get(id=room_id)
            old_status = room.status
            room.status = new_status
            room.save()

            return {
                'success': True,
                'data': {
                    'id': str(room.id),
                    'room_number': room.room_number,
                    'old_status': old_status,
                    'new_status': new_status,
                },
                'message': f'Room status updated to {new_status}'
            }

        except Room.DoesNotExist:
            return {
                'success': False,
                'error': 'Room not found'
            }
        except Exception as e:
            logger.error(f"Error updating room status {room_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

