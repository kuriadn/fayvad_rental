"""
Pytest Configuration for Rental Solution Tests
"""
import pytest
import os
import django
from django.conf import settings

# Setup Django for testing
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rental_project.settings')
django.setup()


@pytest.fixture(scope='session')
def django_db_setup():
    """Setup Django database for testing"""
    pass


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Enable database access for all tests"""
    pass


@pytest.fixture
def test_user():
    """Create a test user"""
    from django.contrib.auth.models import User
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def test_location(test_user):
    """Create a test location"""
    from rental_django.models import Location
    return Location.objects.create(
        name='Test Apartments',
        code='TEST001',
        address='123 Test Street',
        city='Test City',
        manager=test_user,
        is_active=True
    )


@pytest.fixture
def test_tenant(test_location):
    """Create a test tenant"""
    from rental_django.models import Tenant
    return Tenant.objects.create(
        name='John Doe',
        email='john@example.com',
        phone='+1234567890',
        id_number='ID123456',
        current_location=test_location,
        tenant_status='active'
    )


@pytest.fixture
def test_room(test_location):
    """Create a test room"""
    from rental_django.models import Room
    return Room.objects.create(
        number='101',
        location=test_location,
        monthly_rent=1500.00,
        deposit_amount=1500.00,
        status='available'
    )
