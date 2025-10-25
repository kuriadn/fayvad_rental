"""
API Endpoint Tests for Rental Solution
Tests the REST API endpoints and FBS-enhanced actions
"""
import json
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from rental_django.models import Location, Tenant, Room, RentalAgreement


class APITestCase(TestCase):
    """Base test case for API tests"""
    
    def setUp(self):
        """Set up test data and API client"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test location
        self.location = Location.objects.create(
            name='Test Apartments',
            code='TEST001',
            address='123 Test Street',
            city='Test City',
            manager=self.user,
            is_active=True
        )
        
        # Create test tenant
        self.tenant = Tenant.objects.create(
            name='John Doe',
            email='john@example.com',
            phone='+1234567890',
            id_number='ID123456',
            current_location=self.location,
            tenant_status='active'
        )
        
        # Create test room
        self.room = Room.objects.create(
            number='101',
            location=self.location,
            monthly_rent=1500.00,
            deposit_amount=1500.00,
            status='available'
        )
        
        # Authenticate the client
        self.client.force_authenticate(user=self.user)


class LocationAPITests(APITestCase):
    """Test Location API endpoints"""
    
    def test_location_list_endpoint(self):
        """Test GET /api/locations/ endpoint"""
        url = reverse('location-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)
        self.assertIn('results', response.data['data'])
    
    def test_location_create_endpoint(self):
        """Test POST /api/locations/ endpoint"""
        url = reverse('location-list')
        data = {
            'name': 'New Apartments',
            'code': 'NEW001',
            'address': '456 New Street',
            'city': 'New City'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('data', response.data)
        self.assertEqual(response.data['data']['name'], 'New Apartments')
    
    def test_location_detail_endpoint(self):
        """Test GET /api/locations/{id}/ endpoint"""
        url = reverse('location-detail', args=[self.location.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['name'], 'Test Apartments')
    
    def test_location_update_endpoint(self):
        """Test PUT /api/locations/{id}/ endpoint"""
        url = reverse('location-detail', args=[self.location.id])
        data = {
            'name': 'Updated Apartments',
            'code': 'TEST001',
            'address': 'Updated Address',
            'city': 'Updated City'
        }
        
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['name'], 'Updated Apartments')


class TenantAPITests(APITestCase):
    """Test Tenant API endpoints"""
    
    def test_tenant_list_endpoint(self):
        """Test GET /api/tenants/ endpoint"""
        url = reverse('tenant-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)
    
    def test_tenant_create_endpoint(self):
        """Test POST /api/tenants/ endpoint"""
        url = reverse('tenant-list')
        data = {
            'name': 'Jane Smith',
            'email': 'jane@example.com',
            'phone': '+0987654321',
            'id_number': 'ID654321'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['data']['name'], 'Jane Smith')


class RoomAPITests(APITestCase):
    """Test Room API endpoints"""
    
    def test_room_list_endpoint(self):
        """Test GET /api/rooms/ endpoint"""
        url = reverse('room-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)
    
    def test_room_create_endpoint(self):
        """Test POST /api/rooms/ endpoint"""
        url = reverse('room-list')
        data = {
            'number': '201',
            'location': self.location.id,
            'monthly_rent': 2000.00,
            'deposit_amount': 2000.00
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['data']['number'], '201')


class RentalAgreementAPITests(APITestCase):
    """Test Rental Agreement API endpoints"""
    
    def test_rental_list_endpoint(self):
        """Test GET /api/rentals/ endpoint"""
        url = reverse('rentalagreement-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)
    
    def test_rental_create_endpoint(self):
        """Test POST /api/rentals/ endpoint"""
        url = reverse('rentalagreement-list')
        data = {
            'tenant': self.tenant.id,
            'room': self.room.id,
            'start_date': '2024-01-01',
            'monthly_rent': 1500.00,
            'deposit_amount': 1500.00
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['data']['monthly_rent'], '1500.00')


if __name__ == '__main__':
    import pytest
    pytest.main([__file__])
