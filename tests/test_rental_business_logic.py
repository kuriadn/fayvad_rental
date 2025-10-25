"""
Unit Tests for Core Rental Business Logic
Tests all rental business operations, validations, and calculations
"""
import pytest
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import date, timedelta

from rental_django.models import (
    Location, Tenant, Room, RentalAgreement, Payment, 
    MaintenanceRequest, Document, Contract, ActivityLog
)
from rental_django.services import RentalService
from rental_django.sequences import SequenceManager


class RentalBusinessLogicTestCase(TestCase):
    """Base test case for rental business logic tests"""
    
    def setUp(self):
        """Set up test data"""
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
            monthly_rent=Decimal('1500.00'),
            deposit_amount=Decimal('1500.00'),
            status='available'
        )
        
        # Create rental service
        self.rental_service = RentalService()


class LocationModelTests(RentalBusinessLogicTestCase):
    """Test Location model business logic"""
    
    def test_location_creation(self):
        """Test basic location creation"""
        location = Location.objects.create(
            name='New Apartments',
            code='NEW001',
            address='456 New Street',
            city='New City',
            manager=self.user
        )
        
        self.assertEqual(location.name, 'New Apartments')
        self.assertEqual(location.code, 'NEW001')
        self.assertTrue(location.is_active)
        self.assertFalse(location.setup_complete)
        self.assertEqual(location.room_count, 0)
        self.assertEqual(location.occupied_count, 0)
        self.assertEqual(location.available_count, 0)
    
    def test_location_code_validation(self):
        """Test location code format validation"""
        # Valid code
        valid_location = Location(
            name='Valid Apartments',
            code='VALID01',
            city='Valid City'
        )
        valid_location.full_clean()
        
        # Invalid code - too long
        invalid_location = Location(
            name='Invalid Apartments',
            code='INVALIDCODE123',  # Too long
            city='Invalid City'
        )
        with self.assertRaises(ValidationError):
            invalid_location.full_clean()
        
        # Invalid code - wrong characters
        invalid_location2 = Location(
            name='Invalid Apartments 2',
            code='invalid-01',  # Lowercase and hyphen
            city='Invalid City 2'
        )
        with self.assertRaises(ValidationError):
            invalid_location2.full_clean()
    
    def test_location_business_rules(self):
        """Test location business rule validations"""
        # Cannot complete setup without rooms
        self.location.setup_complete = True
        with self.assertRaises(ValidationError):
            self.location.full_clean()
        
        # Cannot deactivate with occupied rooms
        self.room.status = 'occupied'
        self.room.save()
        self.location.occupied_count = 1
        self.location.is_active = False
        with self.assertRaises(ValidationError):
            self.location.full_clean()
    
    def test_location_statistics_update(self):
        """Test location statistics calculation"""
        # Add more rooms
        room2 = Room.objects.create(
            number='102',
            location=self.location,
            monthly_rent=Decimal('1600.00'),
            deposit_amount=Decimal('1600.00'),
            status='available'
        )
        
        room3 = Room.objects.create(
            number='103',
            location=self.location,
            monthly_rent=Decimal('1700.00'),
            deposit_amount=Decimal('1700.00'),
            status='occupied'
        )
        
        # Update statistics
        self.location.update_statistics()
        self.location.refresh_from_db()
        
        self.assertEqual(self.location.room_count, 3)
        self.assertEqual(self.location.occupied_count, 1)
        self.assertEqual(self.location.available_count, 2)
        self.assertEqual(self.location.monthly_revenue, Decimal('4800.00'))
        self.assertAlmostEqual(self.location.occupancy_rate, 1/3, places=2)


class TenantModelTests(RentalBusinessLogicTestCase):
    """Test Tenant model business logic"""
    
    def test_tenant_creation(self):
        """Test basic tenant creation"""
        tenant = Tenant.objects.create(
            name='Jane Smith',
            email='jane@example.com',
            phone='+0987654321',
            id_number='ID654321',
            current_location=self.location
        )
        
        self.assertEqual(tenant.name, 'Jane Smith')
        self.assertEqual(tenant.email, 'jane@example.com')
        self.assertEqual(tenant.tenant_status, 'prospective')
        self.assertIsNone(tenant.current_room)
    
    def test_tenant_phone_validation(self):
        """Test tenant phone number validation"""
        # Valid phone numbers
        valid_phones = [
            '+1234567890',
            '+12345678901',
            '1234567890',
            '12345678901'
        ]
        
        for phone in valid_phones:
            with self.subTest(phone=phone):
                tenant = Tenant(
                    name='Phone Test',
                    email='phone@test.com',
                    phone=phone,
                    id_number='PHONE123'
                )
                tenant.full_clean()
        
        # Invalid phone numbers
        invalid_phones = [
            '123',  # Too short
            '12345678901234567890',  # Too long
            'abc123def',  # Contains letters
            '123-456-7890'  # Contains hyphens
        ]
        
        for phone in invalid_phones:
            with self.subTest(phone=phone):
                tenant = Tenant(
                    name='Phone Test',
                    email='phone@test.com',
                    phone=phone,
                    id_number='PHONE123'
                )
                with self.assertRaises(ValidationError):
                    tenant.full_clean()
    
    def test_tenant_status_transitions(self):
        """Test tenant status transitions"""
        # Prospective -> Active
        self.tenant.tenant_status = 'active'
        self.tenant.current_room = self.room
        self.tenant.save()
        
        self.assertEqual(self.tenant.tenant_status, 'active')
        self.assertIsNotNone(self.tenant.current_room)
        
        # Active -> Notice
        self.tenant.tenant_status = 'notice'
        self.tenant.save()
        
        self.assertEqual(self.tenant.tenant_status, 'notice')
        
        # Notice -> Terminated
        self.tenant.tenant_status = 'terminated'
        self.tenant.save()
        
        self.assertEqual(self.tenant.tenant_status, 'terminated')


class RoomModelTests(RentalBusinessLogicTestCase):
    """Test Room model business logic"""
    
    def test_room_creation(self):
        """Test basic room creation"""
        room = Room.objects.create(
            number='201',
            location=self.location,
            monthly_rent=Decimal('2000.00'),
            deposit_amount=Decimal('2000.00'),
            status='available'
        )
        
        self.assertEqual(room.number, '201')
        self.assertEqual(room.location, self.location)
        self.assertEqual(room.monthly_rent, Decimal('2000.00'))
        self.assertEqual(room.deposit_amount, Decimal('2000.00'))
        self.assertEqual(room.status, 'available')
    
    def test_room_status_transitions(self):
        """Test room status transitions"""
        # Available -> Occupied
        self.room.status = 'occupied'
        self.room.current_tenant = self.tenant
        self.room.save()
        
        self.assertEqual(self.room.status, 'occupied')
        self.assertIsNotNone(self.room.current_tenant)
        
        # Occupied -> Maintenance
        self.room.status = 'maintenance'
        self.room.current_tenant = None
        self.room.save()
        
        self.assertEqual(self.room.status, 'maintenance')
        self.assertIsNone(self.room.current_tenant)
        
        # Maintenance -> Available
        self.room.status = 'available'
        self.room.save()
        
        self.assertEqual(self.room.status, 'available')
    
    def test_room_rent_validation(self):
        """Test room rent validation"""
        # Valid rent amounts
        valid_rents = [
            Decimal('100.00'),
            Decimal('1000.00'),
            Decimal('5000.00')
        ]
        
        for rent in valid_rents:
            with self.subTest(rent=rent):
                room = Room(
                    number='Rent Test',
                    location=self.location,
                    monthly_rent=rent,
                    deposit_amount=rent
                )
                room.full_clean()
        
        # Invalid rent amounts
        invalid_rents = [
            Decimal('-100.00'),  # Negative
            Decimal('0.00'),     # Zero
        ]
        
        for rent in invalid_rents:
            with self.subTest(rent=rent):
                room = Room(
                    number='Rent Test',
                    location=self.location,
                    monthly_rent=rent,
                    deposit_amount=rent
                )
                with self.assertRaises(ValidationError):
                    room.full_clean()


class RentalAgreementModelTests(RentalBusinessLogicTestCase):
    """Test RentalAgreement model business logic"""
    
    def test_rental_agreement_creation(self):
        """Test basic rental agreement creation"""
        rental = RentalAgreement.objects.create(
            tenant=self.tenant,
            room=self.room,
            start_date=date.today(),
            monthly_rent=Decimal('1500.00'),
            deposit_amount=Decimal('1500.00'),
            state='draft'
        )
        
        self.assertEqual(rental.tenant, self.tenant)
        self.assertEqual(rental.room, self.room)
        self.assertEqual(rental.state, 'draft')
        self.assertEqual(rental.monthly_rent, Decimal('1500.00'))
        self.assertEqual(rental.deposit_amount, Decimal('1500.00'))
    
    def test_rental_agreement_state_transitions(self):
        """Test rental agreement state transitions"""
        rental = RentalAgreement.objects.create(
            tenant=self.tenant,
            room=self.room,
            start_date=date.today(),
            monthly_rent=Decimal('1500.00'),
            deposit_amount=Decimal('1500.00'),
            state='draft'
        )
        
        # Draft -> Active
        rental.state = 'active'
        rental.activation_date = timezone.now()
        rental.save()
        
        self.assertEqual(rental.state, 'active')
        self.assertIsNotNone(rental.activation_date)
        
        # Active -> Notice
        rental.state = 'notice'
        rental.notice_date = timezone.now()
        rental.save()
        
        self.assertEqual(rental.state, 'notice')
        self.assertIsNotNone(rental.notice_date)
        
        # Notice -> Terminated
        rental.state = 'terminated'
        rental.termination_date = timezone.now()
        rental.save()
        
        self.assertEqual(rental.state, 'terminated')
        self.assertIsNotNone(rental.termination_date)
    
    def test_rental_agreement_date_validation(self):
        """Test rental agreement date validation"""
        # Valid dates
        today = date.today()
        future_date = today + timedelta(days=30)
        
        rental = RentalAgreement(
            tenant=self.tenant,
            room=self.room,
            start_date=future_date,
            monthly_rent=Decimal('1500.00'),
            deposit_amount=Decimal('1500.00')
        )
        rental.full_clean()
        
        # Invalid dates
        past_date = today - timedelta(days=30)
        
        rental2 = RentalAgreement(
            tenant=self.tenant,
            room=self.room,
            start_date=past_date,
            monthly_rent=Decimal('1500.00'),
            deposit_amount=Decimal('1500.00')
        )
        with self.assertRaises(ValidationError):
            rental2.full_clean()
    
    def test_rental_agreement_financial_calculations(self):
        """Test rental agreement financial calculations"""
        rental = RentalAgreement.objects.create(
            tenant=self.tenant,
            room=self.room,
            start_date=date.today(),
            monthly_rent=Decimal('1500.00'),
            deposit_amount=Decimal('1500.00'),
            state='active'
        )
        
        # Test total rent calculation
        total_rent = rental.calculate_total_rent()
        self.assertIsInstance(total_rent, Decimal)
        self.assertGreater(total_rent, 0)
        
        # Test outstanding balance
        outstanding = rental.calculate_outstanding_balance()
        self.assertIsInstance(outstanding, Decimal)
        self.assertGreaterEqual(outstanding, 0)


class PaymentModelTests(RentalBusinessLogicTestCase):
    """Test Payment model business logic"""
    
    def setUp(self):
        """Set up payment test data"""
        super().setUp()
        
        # Create rental agreement
        self.rental = RentalAgreement.objects.create(
            tenant=self.tenant,
            room=self.room,
            start_date=date.today(),
            monthly_rent=Decimal('1500.00'),
            deposit_amount=Decimal('1500.00'),
            state='active'
        )
    
    def test_payment_creation(self):
        """Test basic payment creation"""
        payment = Payment.objects.create(
            rental_agreement=self.rental,
            amount=Decimal('1500.00'),
            payment_method='mpesa',
            reference_number='MPESA123456',
            payment_date=date.today()
        )
        
        self.assertEqual(payment.rental_agreement, self.rental)
        self.assertEqual(payment.amount, Decimal('1500.00'))
        self.assertEqual(payment.payment_method, 'mpesa')
        self.assertEqual(payment.reference_number, 'MPESA123456')
        self.assertEqual(payment.status, 'pending')
    
    def test_payment_method_validation(self):
        """Test payment method validation"""
        # Valid payment methods
        valid_methods = ['mpesa', 'airtel', 'bank', 'cash', 'card']
        
        for method in valid_methods:
            with self.subTest(method=method):
                payment = Payment(
                    rental_agreement=self.rental,
                    amount=Decimal('100.00'),
                    payment_method=method,
                    reference_number=f'{method.upper()}123'
                )
                payment.full_clean()
        
        # Invalid payment method
        payment = Payment(
            rental_agreement=self.rental,
            amount=Decimal('100.00'),
            payment_method='invalid_method',
            reference_number='INVALID123'
        )
        with self.assertRaises(ValidationError):
            payment.full_clean()
    
    def test_payment_amount_validation(self):
        """Test payment amount validation"""
        # Valid amounts
        valid_amounts = [
            Decimal('100.00'),
            Decimal('1500.00'),
            Decimal('5000.00')
        ]
        
        for amount in valid_amounts:
            with self.subTest(amount=amount):
                payment = Payment(
                    rental_agreement=self.rental,
                    amount=amount,
                    payment_method='mpesa',
                    reference_number=f'MPESA{amount}'
                )
                payment.full_clean()
        
        # Invalid amounts
        invalid_amounts = [
            Decimal('-100.00'),  # Negative
            Decimal('0.00'),     # Zero
        ]
        
        for amount in invalid_amounts:
            with self.subTest(amount=amount):
                payment = Payment(
                    rental_agreement=self.rental,
                    amount=amount,
                    payment_method='mpesa',
                    reference_number=f'MPESA{amount}'
                )
                with self.assertRaises(ValidationError):
                    payment.full_clean()
    
    def test_payment_validation_workflow(self):
        """Test payment validation workflow"""
        payment = Payment.objects.create(
            rental_agreement=self.rental,
            amount=Decimal('1500.00'),
            payment_method='mpesa',
            reference_number='MPESA123456',
            payment_date=date.today(),
            status='pending'
        )
        
        # Validate payment
        payment.status = 'validated'
        payment.validation_date = timezone.now()
        payment.validated_by = self.user
        payment.save()
        
        self.assertEqual(payment.status, 'validated')
        self.assertIsNotNone(payment.validation_date)
        self.assertEqual(payment.validated_by, self.user)
        
        # Unvalidate payment
        payment.status = 'pending'
        payment.validation_date = None
        payment.validated_by = None
        payment.save()
        
        self.assertEqual(payment.status, 'pending')
        self.assertIsNone(payment.validation_date)
        self.assertIsNone(payment.validated_by)


class MaintenanceRequestModelTests(RentalBusinessLogicTestCase):
    """Test MaintenanceRequest model business logic"""
    
    def test_maintenance_request_creation(self):
        """Test basic maintenance request creation"""
        request = MaintenanceRequest.objects.create(
            title='Fix Leaking Faucet',
            description='The faucet in room 101 is leaking',
            location=self.location,
            room=self.room,
            reported_by=self.tenant,
            priority='medium'
        )
        
        self.assertEqual(request.title, 'Fix Leaking Faucet')
        self.assertEqual(request.location, self.location)
        self.assertEqual(request.room, self.room)
        self.assertEqual(request.reported_by, self.tenant)
        self.assertEqual(request.priority, 'medium')
        self.assertEqual(request.status, 'open')
    
    def test_maintenance_priority_validation(self):
        """Test maintenance priority validation"""
        # Valid priorities
        valid_priorities = ['low', 'medium', 'high', 'urgent']
        
        for priority in valid_priorities:
            with self.subTest(priority=priority):
                request = MaintenanceRequest(
                    title='Priority Test',
                    description='Testing priority validation',
                    location=self.location,
                    priority=priority
                )
                request.full_clean()
        
        # Invalid priority
        request = MaintenanceRequest(
            title='Invalid Priority',
            description='Testing invalid priority',
            location=self.location,
            priority='invalid_priority'
        )
        with self.assertRaises(ValidationError):
            request.full_clean()
    
    def test_maintenance_status_transitions(self):
        """Test maintenance status transitions"""
        request = MaintenanceRequest.objects.create(
            title='Status Test',
            description='Testing status transitions',
            location=self.location,
            priority='medium'
        )
        
        # Open -> Assigned
        request.status = 'assigned'
        request.assigned_to = self.user
        request.assigned_date = timezone.now()
        request.save()
        
        self.assertEqual(request.status, 'assigned')
        self.assertIsNotNone(request.assigned_to)
        self.assertIsNotNone(request.assigned_date)
        
        # Assigned -> In Progress
        request.status = 'in_progress'
        request.started_date = timezone.now()
        request.save()
        
        self.assertEqual(request.status, 'in_progress')
        self.assertIsNotNone(request.started_date)
        
        # In Progress -> Completed
        request.status = 'completed'
        request.completed_date = timezone.now()
        request.save()
        
        self.assertEqual(request.status, 'completed')
        self.assertIsNotNone(request.completed_date)


class RentalServiceTests(RentalBusinessLogicTestCase):
    """Test RentalService business logic"""
    
    def test_activate_rental(self):
        """Test rental activation"""
        rental = RentalAgreement.objects.create(
            tenant=self.tenant,
            room=self.room,
            start_date=date.today(),
            monthly_rent=Decimal('1500.00'),
            deposit_amount=Decimal('1500.00'),
            state='draft'
        )
        
        result = self.rental_service.activate_rental(rental.id)
        
        self.assertTrue(result['success'])
        rental.refresh_from_db()
        self.assertEqual(rental.state, 'active')
        self.assertIsNotNone(rental.activation_date)
    
    def test_give_notice(self):
        """Test giving notice to tenant"""
        rental = RentalAgreement.objects.create(
            tenant=self.tenant,
            room=self.room,
            start_date=date.today(),
            monthly_rent=Decimal('1500.00'),
            deposit_amount=Decimal('1500.00'),
            state='active'
        )
        
        result = self.rental_service.give_notice(rental.id)
        
        self.assertTrue(result['success'])
        rental.refresh_from_db()
        self.assertEqual(rental.state, 'notice')
        self.assertIsNotNone(rental.notice_date)
    
    def test_terminate_rental(self):
        """Test rental termination"""
        rental = RentalAgreement.objects.create(
            tenant=self.tenant,
            room=self.room,
            start_date=date.today(),
            monthly_rent=Decimal('1500.00'),
            deposit_amount=Decimal('1500.00'),
            state='notice'
        )
        
        result = self.rental_service.terminate_rental(rental.id, 'Tenant moved out')
        
        self.assertTrue(result['success'])
        rental.refresh_from_db()
        self.assertEqual(rental.state, 'terminated')
        self.assertIsNotNone(rental.termination_date)
        self.assertEqual(rental.termination_reason, 'Tenant moved out')


class SequenceManagerTests(RentalBusinessLogicTestCase):
    """Test SequenceManager functionality"""
    
    def test_sequence_generation(self):
        """Test sequence number generation"""
        sequence_manager = SequenceManager()
        
        # Generate location code
        location_code = sequence_manager.generate_location_code()
        self.assertIsInstance(location_code, str)
        self.assertTrue(location_code.startswith('LOC'))
        
        # Generate tenant ID
        tenant_id = sequence_manager.generate_tenant_id()
        self.assertIsInstance(tenant_id, str)
        self.assertTrue(tenant_id.startswith('TEN'))
        
        # Generate rental reference
        rental_ref = sequence_manager.generate_rental_reference()
        self.assertIsInstance(rental_ref, str)
        self.assertTrue(rental_ref.startswith('RENT'))


if __name__ == '__main__':
    pytest.main([__file__])
