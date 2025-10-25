"""
Test Core Services
Pure Django service layer tests
"""

from django.test import TestCase
from decimal import Decimal
from datetime import date, timedelta

from core_services import (
    TenantService,
    PropertyService,
    RentalService,
    PaymentService,
    MaintenanceService
)
from tenants.models import Tenant
from properties.models import Location, Room
from rentals.models import RentalAgreement
from payments.models import Payment
from maintenance.models import MaintenanceRequest
from accounts.models import User


class TenantServiceTest(TestCase):
    """Test TenantService"""
    
    def setUp(self):
        self.tenant = Tenant.objects.create(
            name="Test Tenant",
            email="test@example.com",
            tenant_status="active"
        )
    
    def test_get_tenants(self):
        """Test get_tenants service method"""
        result = TenantService.get_tenants()
        self.assertTrue(result['success'])
        self.assertEqual(len(result['data']), 1)
        self.assertEqual(result['total'], 1)
    
    def test_get_tenant(self):
        """Test get_tenant service method"""
        result = TenantService.get_tenant(str(self.tenant.id))
        self.assertTrue(result['success'])
        self.assertEqual(result['data']['name'], "Test Tenant")
    
    def test_create_tenant(self):
        """Test create_tenant service method"""
        data = {
            'name': 'New Tenant',
            'email': 'new@example.com',
            'phone': '+254700000000',
            'tenant_type': 'professional'
        }
        result = TenantService.create_tenant(data)
        self.assertTrue(result['success'])
        self.assertEqual(result['data']['name'], 'New Tenant')
    
    def test_update_tenant(self):
        """Test update_tenant service method"""
        result = TenantService.update_tenant(
            str(self.tenant.id),
            {'email': 'updated@example.com'}
        )
        self.assertTrue(result['success'])
        
        # Verify update
        self.tenant.refresh_from_db()
        self.assertEqual(self.tenant.email, 'updated@example.com')
    
    def test_validate_tenant_deletion(self):
        """Test validate_tenant_deletion service method"""
        result = TenantService.validate_tenant_deletion(str(self.tenant.id))
        self.assertTrue(result['success'])
        self.assertTrue(result['data']['can_delete'])


class PropertyServiceTest(TestCase):
    """Test PropertyService"""
    
    def setUp(self):
        self.location = Location.objects.create(
            name="Test Location",
            code="TL001"
        )
        self.room = Room.objects.create(
            room_number="101",
            location=self.location,
            status="available"
        )
    
    def test_get_locations(self):
        """Test get_locations service method"""
        result = PropertyService.get_locations()
        self.assertTrue(result['success'])
        self.assertEqual(len(result['data']), 1)
    
    def test_get_location(self):
        """Test get_location service method"""
        result = PropertyService.get_location(str(self.location.id))
        self.assertTrue(result['success'])
        self.assertEqual(result['data']['code'], "TL001")
    
    def test_get_rooms(self):
        """Test get_rooms service method"""
        result = PropertyService.get_rooms()
        self.assertTrue(result['success'])
        self.assertEqual(len(result['data']), 1)
    
    def test_get_room(self):
        """Test get_room service method"""
        result = PropertyService.get_room(str(self.room.id))
        self.assertTrue(result['success'])
        self.assertEqual(result['data']['room_number'], "101")
    
    def test_update_room_status(self):
        """Test update_room_status service method"""
        result = PropertyService.update_room_status(
            str(self.room.id),
            "occupied"
        )
        self.assertTrue(result['success'])
        
        # Verify update
        self.room.refresh_from_db()
        self.assertEqual(self.room.status, "occupied")


class RentalServiceTest(TestCase):
    """Test RentalService"""
    
    def setUp(self):
        self.tenant = Tenant.objects.create(
            name="Tenant",
            email="tenant@example.com"
        )
        self.location = Location.objects.create(
            name="Location",
            code="LOC001"
        )
        self.room = Room.objects.create(
            room_number="101",
            location=self.location,
            status="available"
        )
        self.agreement = RentalAgreement.objects.create(
            tenant=self.tenant,
            room=self.room,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=365),
            rent_amount=Decimal("1000.00"),
            deposit_amount=Decimal("1000.00"),
            status="draft"
        )
    
    def test_get_rental_agreements(self):
        """Test get_rental_agreements service method"""
        result = RentalService.get_rental_agreements()
        self.assertTrue(result['success'])
        self.assertEqual(len(result['data']), 1)
    
    def test_get_rental_agreement(self):
        """Test get_rental_agreement service method"""
        result = RentalService.get_rental_agreement(str(self.agreement.id))
        self.assertTrue(result['success'])
        self.assertEqual(float(result['data']['rent_amount']), 1000.00)
    
    def test_activate_agreement(self):
        """Test activate_agreement service method"""
        result = RentalService.activate_agreement(str(self.agreement.id))
        self.assertTrue(result['success'])
        
        # Verify activation
        self.agreement.refresh_from_db()
        self.assertEqual(self.agreement.status, "active")
        
        # Verify room status changed
        self.room.refresh_from_db()
        self.assertEqual(self.room.status, "occupied")
    
    def test_terminate_agreement(self):
        """Test terminate_agreement service method"""
        # First activate
        self.agreement.status = "active"
        self.agreement.save()
        
        # Then terminate
        result = RentalService.terminate_agreement(str(self.agreement.id))
        self.assertTrue(result['success'])
        
        # Verify termination
        self.agreement.refresh_from_db()
        self.assertEqual(self.agreement.status, "terminated")


class PaymentServiceTest(TestCase):
    """Test PaymentService"""
    
    def setUp(self):
        self.tenant = Tenant.objects.create(
            name="Tenant",
            email="tenant@example.com"
        )
        self.payment = Payment.objects.create(
            tenant=self.tenant,
            amount=Decimal("1500.00"),
            payment_method="mpesa",
            status="pending"
        )
    
    def test_get_payments(self):
        """Test get_payments service method"""
        result = PaymentService.get_payments()
        self.assertTrue(result['success'])
        self.assertEqual(len(result['data']), 1)
    
    def test_get_payment(self):
        """Test get_payment service method"""
        result = PaymentService.get_payment(str(self.payment.id))
        self.assertTrue(result['success'])
        self.assertEqual(float(result['data']['amount']), 1500.00)
    
    def test_complete_payment(self):
        """Test complete_payment service method"""
        result = PaymentService.complete_payment(
            str(self.payment.id),
            transaction_id="TXN123456"
        )
        self.assertTrue(result['success'])
        
        # Verify completion
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, "completed")
        self.assertEqual(self.payment.transaction_id, "TXN123456")


class MaintenanceServiceTest(TestCase):
    """Test MaintenanceService"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email="admin@example.com",
            password="testpass"
        )
        self.tenant = Tenant.objects.create(
            name="Tenant",
            email="tenant@example.com"
        )
        self.location = Location.objects.create(
            name="Location",
            code="LOC001"
        )
        self.room = Room.objects.create(
            room_number="101",
            location=self.location
        )
        self.request = MaintenanceRequest.objects.create(
            title="Fix leak",
            description="Water leak in bathroom",
            tenant=self.tenant,
            room=self.room,
            created_by=self.user,
            priority="high",
            status="pending"
        )
    
    def test_get_maintenance_requests(self):
        """Test get_maintenance_requests service method"""
        result = MaintenanceService.get_maintenance_requests()
        self.assertTrue(result['success'])
        self.assertEqual(len(result['data']), 1)
    
    def test_get_maintenance_request(self):
        """Test get_maintenance_request service method"""
        result = MaintenanceService.get_maintenance_request(str(self.request.id))
        self.assertTrue(result['success'])
        self.assertEqual(result['data']['title'], "Fix leak")
    
    def test_assign_technician(self):
        """Test assign_technician service method"""
        result = MaintenanceService.assign_technician(
            str(self.request.id),
            "John Technician"
        )
        self.assertTrue(result['success'])
        
        # Verify assignment
        self.request.refresh_from_db()
        self.assertEqual(self.request.assigned_to, "John Technician")
        self.assertEqual(self.request.status, "in_progress")
    
    def test_complete_request(self):
        """Test complete_request service method"""
        # First assign
        self.request.assign_technician("Technician")
        
        # Then complete
        result = MaintenanceService.complete_request(
            str(self.request.id),
            resolution_notes="Fixed the leak",
            actual_cost=500.00
        )
        self.assertTrue(result['success'])
        
        # Verify completion
        self.request.refresh_from_db()
        self.assertEqual(self.request.status, "completed")
        self.assertEqual(self.request.resolution_notes, "Fixed the leak")


# Run tests with: python manage.py test tests.test_services

