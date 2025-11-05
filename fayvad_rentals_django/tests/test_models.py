"""
Test Django Models
Pure Django rental management system
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import date, timedelta

from tenants.models import Tenant, TenantStatus
from properties.models import Location, Room, RoomStatus
from rentals.models import RentalAgreement, AgreementStatus
from payments.models import Payment, PaymentStatus
from maintenance.models import MaintenanceRequest, MaintenanceStatus, Priority
from accounts.models import User


class TenantModelTest(TestCase):
    """Test Tenant model"""
    
    def setUp(self):
        self.tenant = Tenant.objects.create(
            name="John Doe",
            email="john@example.com",
            phone="+254712345678",
            tenant_type="student",
            tenant_status="prospective"
        )
    
    def test_tenant_creation(self):
        """Test tenant is created correctly"""
        self.assertEqual(self.tenant.name, "John Doe")
        self.assertEqual(self.tenant.tenant_status, "prospective")
        self.assertIsNotNone(self.tenant.id)
    
    def test_tenant_financial_summary(self):
        """Test financial summary property"""
        summary = self.tenant.financial_summary
        self.assertEqual(summary['account_balance'], 0.0)
        self.assertEqual(summary['total_payments'], 0.0)
    
    def test_tenant_can_assign_room(self):
        """Test can_assign_room property"""
        self.assertTrue(self.tenant.can_assign_room)
        self.tenant.tenant_status = "blacklisted"
        self.assertFalse(self.tenant.can_assign_room)


class LocationModelTest(TestCase):
    """Test Location model"""
    
    def setUp(self):
        self.location = Location.objects.create(
            name="Campus Complex",
            code="CC001",
            city="Nairobi",
            is_active=True
        )
    
    def test_location_creation(self):
        """Test location is created correctly"""
        self.assertEqual(self.location.code, "CC001")
        self.assertTrue(self.location.is_active)
    
    def test_location_code_uppercase(self):
        """Test code is uppercase"""
        location = Location(name="Test", code="test123")
        location.clean()
        self.assertEqual(location.code, "TEST123")
    
    def test_occupancy_rate(self):
        """Test occupancy rate calculation"""
        self.assertEqual(self.location.occupancy_rate, 0.0)


class RoomModelTest(TestCase):
    """Test Room model"""
    
    def setUp(self):
        self.location = Location.objects.create(
            name="Building A",
            code="BA001"
        )
        self.room = Room.objects.create(
            room_number="101",
            location=self.location,
            room_type="single",
            capacity=1,
            status="available"
        )
    
    def test_room_creation(self):
        """Test room is created correctly"""
        self.assertEqual(self.room.room_number, "101")
        self.assertEqual(self.room.capacity, 1)
    
    def test_room_availability(self):
        """Test is_available property"""
        self.assertTrue(self.room.is_available)
        self.room.status = "occupied"
        self.assertFalse(self.room.is_available)
    
    def test_full_identifier(self):
        """Test full room identifier"""
        identifier = self.room.full_room_identifier
        self.assertEqual(identifier, "BA001-101")


class RentalAgreementModelTest(TestCase):
    """Test RentalAgreement model"""
    
    def setUp(self):
        self.tenant = Tenant.objects.create(
            name="Jane Smith",
            email="jane@example.com"
        )
        self.location = Location.objects.create(
            name="Building B",
            code="BB001"
        )
        self.room = Room.objects.create(
            room_number="201",
            location=self.location
        )
        self.agreement = RentalAgreement.objects.create(
            tenant=self.tenant,
            room=self.room,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=365),
            rent_amount=Decimal("1500.00"),
            deposit_amount=Decimal("1500.00"),
            status="draft"
        )
    
    def test_agreement_creation(self):
        """Test agreement is created correctly"""
        self.assertEqual(self.agreement.rent_amount, Decimal("1500.00"))
        self.assertIsNotNone(self.agreement.agreement_number)
    
    def test_agreement_duration(self):
        """Test duration calculations"""
        self.assertEqual(self.agreement.duration_days, 365)
        self.assertAlmostEqual(self.agreement.duration_months, 12.0, places=1)
    
    def test_agreement_activation(self):
        """Test agreement activation"""
        self.agreement.activate_agreement()
        self.assertEqual(self.agreement.status, "active")
        # Room should be marked as occupied
        self.room.refresh_from_db()
        self.assertEqual(self.room.status, "occupied")
    
    def test_total_contract_value(self):
        """Test total contract value calculation"""
        value = self.agreement.total_contract_value
        expected = 1500 * 12 + 1500  # rent * months + deposit
        self.assertAlmostEqual(value, expected, places=0)


class PaymentModelTest(TestCase):
    """Test Payment model"""
    
    def setUp(self):
        self.tenant = Tenant.objects.create(
            name="Bob Johnson",
            email="bob@example.com"
        )
        self.payment = Payment.objects.create(
            tenant=self.tenant,
            amount=Decimal("1500.00"),
            payment_method="mpesa",
            status="pending"
        )
    
    def test_payment_creation(self):
        """Test payment is created correctly"""
        self.assertEqual(self.payment.amount, Decimal("1500.00"))
        self.assertIsNotNone(self.payment.payment_number)
    
    def test_payment_completion(self):
        """Test payment completion"""
        self.payment.complete_payment(transaction_id="TXN123")
        self.assertEqual(self.payment.status, "completed")
        self.assertEqual(self.payment.transaction_id, "TXN123")
        self.assertIsNotNone(self.payment.processed_date)
    
    def test_payment_status_checks(self):
        """Test payment status properties"""
        self.assertTrue(self.payment.is_pending)
        self.assertFalse(self.payment.is_completed)


class MaintenanceRequestModelTest(TestCase):
    """Test MaintenanceRequest model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email="admin@example.com",
            password="testpass"
        )
        self.tenant = Tenant.objects.create(
            name="Alice Brown",
            email="alice@example.com"
        )
        self.location = Location.objects.create(
            name="Building C",
            code="BC001"
        )
        self.room = Room.objects.create(
            room_number="301",
            location=self.location
        )
        self.request = MaintenanceRequest.objects.create(
            title="Broken window",
            description="Window is cracked",
            tenant=self.tenant,
            room=self.room,
            created_by=self.user,
            priority="high",
            status="pending"
        )
    
    def test_request_creation(self):
        """Test maintenance request is created correctly"""
        self.assertEqual(self.request.title, "Broken window")
        self.assertEqual(self.request.priority, "high")
        self.assertIsNotNone(self.request.request_number)
    
    def test_request_assignment(self):
        """Test technician assignment"""
        self.request.assign_technician("John Technician")
        self.assertEqual(self.request.assigned_to, "John Technician")
        self.assertEqual(self.request.status, "in_progress")
    
    def test_request_completion(self):
        """Test request completion"""
        self.request.assign_technician("Technician")
        self.request.complete_request(
            resolution_notes="Fixed the window",
            actual_cost=Decimal("500.00")
        )
        self.assertEqual(self.request.status, "completed")
        self.assertIsNotNone(self.request.completed_date)
    
    def test_overdue_detection(self):
        """Test overdue detection based on priority"""
        # For high priority, overdue after 3 days
        self.assertEqual(self.request.priority, "high")
        # Days pending is 0 for new request
        self.assertFalse(self.request.is_overdue)


# Run tests with: python manage.py test tests.test_models

