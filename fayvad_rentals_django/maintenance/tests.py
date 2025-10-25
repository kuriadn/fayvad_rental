"""
Maintenance request tests
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from maintenance.models import MaintenanceRequest, MaintenanceStatus, Priority
from tenants.models import Tenant
from properties.models import Room, Location
from core_services.maintenance_service import MaintenanceService

User = get_user_model()


class MaintenanceRequestModelTest(TestCase):
    """Test MaintenanceRequest model methods"""

    def setUp(self):
        # Create test data
        self.location = Location.objects.create(name="Test Building", address="123 Test St")
        self.room = Room.objects.create(
            room_number="101",
            location=self.location,
            rent_amount=50000.00
        )
        self.tenant = Tenant.objects.create(
            name="Test Tenant",
            email="tenant@test.com",
            phone="1234567890"
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )

        self.request = MaintenanceRequest.objects.create(
            title="Test Maintenance",
            description="Test description",
            tenant=self.tenant,
            room=self.room,
            created_by=self.user,
            priority=Priority.MEDIUM
        )

    def test_request_number_generation(self):
        """Test that request numbers are generated"""
        self.assertIsNotNone(self.request.request_number)
        self.assertTrue(self.request.request_number.startswith('MNT-'))

    def test_status_properties(self):
        """Test status property methods"""
        self.assertTrue(self.request.is_pending)
        self.assertFalse(self.request.is_in_progress)
        self.assertFalse(self.request.is_completed)

    def test_overdue_calculation(self):
        """Test overdue calculation"""
        # New request should not be overdue
        self.assertFalse(self.request.is_overdue)

        # Make request old enough to be overdue
        old_date = timezone.now() - timedelta(days=10)
        self.request.created_at = old_date
        self.request.save()

        # Medium priority should be overdue after 7 days
        self.assertTrue(self.request.is_overdue)


class MaintenanceServiceTest(TestCase):
    """Test MaintenanceService methods"""

    def setUp(self):
        # Create test data similar to model test
        self.location = Location.objects.create(name="Test Building", address="123 Test St")
        self.room = Room.objects.create(
            room_number="101",
            location=self.location,
            rent_amount=50000.00
        )
        self.tenant = Tenant.objects.create(
            name="Test Tenant",
            email="tenant@test.com",
            phone="1234567890"
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            is_staff=True
        )

        self.request = MaintenanceRequest.objects.create(
            title="Test Maintenance",
            description="Test description",
            tenant=self.tenant,
            room=self.room,
            created_by=self.user,
            priority=Priority.MEDIUM
        )

    def test_get_workflow_status(self):
        """Test workflow status retrieval"""
        result = MaintenanceService.get_workflow_status(str(self.request.id), self.user)

        self.assertTrue(result['success'])
        self.assertIn('available_events', result['data'])
        self.assertIn('sla_status', result['data'])

    def test_assign_technician(self):
        """Test technician assignment"""
        result = MaintenanceService.assign_technician(
            str(self.request.id),
            "John Doe",
            self.user
        )

        self.assertTrue(result['success'])
        self.request.refresh_from_db()
        self.assertEqual(self.request.assigned_to, "John Doe")
        self.assertEqual(self.request.status, MaintenanceStatus.IN_PROGRESS)

    def test_complete_request(self):
        """Test request completion"""
        # First assign technician
        MaintenanceService.assign_technician(str(self.request.id), "John Doe", self.user)

        # Then complete
        result = MaintenanceService.complete_request(
            str(self.request.id),
            self.user,
            resolution_notes="Fixed the issue",
            actual_cost=2500.00
        )

        self.assertTrue(result['success'])
        self.request.refresh_from_db()
        self.assertEqual(self.request.status, MaintenanceStatus.COMPLETED)
        self.assertEqual(self.request.resolution_notes, "Fixed the issue")
        self.assertEqual(self.request.actual_cost, 2500.00)
