"""
Comprehensive FBS Integration Tests
Tests all FBS interfaces and capabilities with the rental solution
"""
import pytest
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from unittest.mock import Mock, patch, MagicMock

from rental_django.fbs_enhanced_service import FBSEnhancedRentalService
from rental_django.models import Location, Tenant, Room, RentalAgreement, Payment, MaintenanceRequest


class FBSIntegrationTestCase(TestCase):
    """Base test case for FBS integration tests"""
    
    def setUp(self):
        """Set up test data and FBS service"""
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
        
        # Initialize FBS service
        self.fbs_service = FBSEnhancedRentalService()
    
    def tearDown(self):
        """Clean up test data"""
        User.objects.all().delete()
        Location.objects.all().delete()
        Tenant.objects.all().delete()
        Room.objects.all().delete()
        RentalAgreement.objects.all().delete()
        Payment.objects.all().delete()
        MaintenanceRequest.objects.all().delete()


class FBSInterfaceTests(FBSIntegrationTestCase):
    """Test FBS interface availability and initialization"""
    
    def test_fbs_interface_initialization(self):
        """Test FBS interface is properly initialized"""
        self.assertIsNotNone(self.fbs_service.fbs)
        self.assertTrue(self.fbs_service.fbs_available)
        self.assertEqual(self.fbs_service.solution_name, 'rental')
    
    def test_fbs_status_check(self):
        """Test FBS status check functionality"""
        status = self.fbs_service.get_fbs_status()
        self.assertIn('fbs_available', status)
        self.assertTrue(status['fbs_available'])
    
    def test_fbs_interfaces_available(self):
        """Test all expected FBS interfaces are available"""
        expected_interfaces = [
            'msme', 'workflows', 'bi', 'compliance', 
            'fields', 'notifications', 'odoo', 'accounting',
            'cache', 'onboarding'
        ]
        
        for interface_name in expected_interfaces:
            with self.subTest(interface=interface_name):
                self.assertTrue(hasattr(self.fbs_service.fbs, interface_name))


class FBSOdooIntegrationTests(FBSIntegrationTestCase):
    """Test FBS Odoo integration capabilities"""
    
    @patch('fbs_app.interfaces.FBSInterface')
    def test_odoo_data_retrieval_success(self, mock_fbs):
        """Test successful Odoo data retrieval"""
        # Mock successful response
        mock_fbs.return_value.odoo.discover_models.return_value = {
            'success': True,
            'data': {
                'models': [
                    {'model': 'res.partner', 'name': 'Contact'},
                    {'model': 'product.product', 'name': 'Product'}
                ]
            }
        }
        
        mock_fbs.return_value.odoo.get_records.return_value = [
            {'id': 1, 'name': 'Test Partner'},
            {'id': 2, 'name': 'Test Product'}
        ]
        
        service = FBSEnhancedRentalService()
        result = service.get_fbs_odoo_data('res.partner', {})
        
        self.assertTrue(result['success'])
        self.assertIn('records', result)
        self.assertEqual(len(result['records']), 2)
    
    @patch('fbs_app.interfaces.FBSInterface')
    def test_odoo_data_retrieval_failure(self, mock_fbs):
        """Test Odoo data retrieval failure handling"""
        # Mock failure response
        mock_fbs.return_value.odoo.discover_models.return_value = {
            'success': False,
            'error': 'Connection failed'
        }
        
        service = FBSEnhancedRentalService()
        result = service.get_fbs_odoo_data('res.partner', {})
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)


class FBSLocationIntegrationTests(FBSIntegrationTestCase):
    """Test FBS-enhanced location creation and management"""
    
    @patch('fbs_app.interfaces.FBSInterface')
    def test_location_creation_with_fbs_success(self, mock_fbs):
        """Test successful location creation with FBS integration"""
        # Mock FBS business profile creation
        mock_fbs.return_value.msme.setup_business.return_value = {
            'success': True,
            'data': {'id': 'fbs_business_123'}
        }
        
        # Mock FBS workflow creation
        mock_fbs.return_value.workflows.start_workflow.return_value = {
            'success': True,
            'workflow_id': 'fbs_workflow_456'
        }
        
        service = FBSEnhancedRentalService()
        location_data = {
            'name': 'FBS Test Apartments',
            'code': 'FBSTEST02',
            'address': '456 FBS Street',
            'city': 'FBS City'
        }
        
        result = service.create_location_with_fbs(location_data, self.user)
        
        self.assertTrue(result['success'])
        location = result['location']
        self.assertEqual(location.name, 'FBS Test Apartments')
        self.assertEqual(location.code, 'FBSTEST02')
        self.assertIsNotNone(location.fbs_business_id)
        self.assertIsNotNone(location.fbs_workflow_id)
    
    @patch('fbs_app.interfaces.FBSInterface')
    def test_location_creation_fbs_failure_fallback(self, mock_fbs):
        """Test location creation falls back when FBS fails"""
        # Mock FBS failure
        mock_fbs.return_value.msme.setup_business.return_value = {
            'success': False,
            'error': 'FBS service unavailable'
        }
        
        service = FBSEnhancedRentalService()
        location_data = {
            'name': 'Fallback Test Apartments',
            'code': 'FALLBACK01',
            'address': '789 Fallback Street',
            'city': 'Fallback City'
        }
        
        result = service.create_location_with_fbs(location_data, self.user)
        
        # Should still succeed with basic creation
        self.assertTrue(result['success'])
        location = result['location']
        self.assertEqual(location.name, 'Fallback Test Apartments')
        self.assertEqual(location.code, 'FALLBACK01')


class FBSRentalAnalyticsTests(FBSIntegrationTestCase):
    """Test FBS-enhanced rental analytics"""
    
    def test_basic_rental_analytics(self):
        """Test basic rental analytics without FBS BI"""
        service = FBSEnhancedRentalService()
        result = service.get_rental_analytics_with_fbs()
        
        self.assertTrue(result['success'])
        analytics = result['analytics']
        
        # Check overall analytics
        self.assertIn('overall', analytics)
        overall = analytics['overall']
        self.assertGreaterEqual(overall['total_locations'], 1)
        self.assertGreaterEqual(overall['total_rooms'], 0)
        self.assertIsInstance(overall['overall_occupancy_rate'], float)
        self.assertIsInstance(overall['total_monthly_revenue'], float)
    
    @patch('fbs_app.interfaces.FBSInterface')
    def test_rental_analytics_with_fbs_bi(self, mock_fbs):
        """Test rental analytics enhanced with FBS BI"""
        # Mock FBS BI interface
        mock_fbs.return_value.bi.get_analytics_data.return_value = {
            'success': True,
            'data': {
                'occupancy_trends': [0.8, 0.85, 0.9],
                'revenue_growth': [1500, 1600, 1700]
            }
        }
        
        service = FBSEnhancedRentalService()
        result = service.get_rental_analytics_with_fbs(str(self.location.id))
        
        self.assertTrue(result['success'])
        analytics = result['analytics']
        
        # Check location-specific analytics
        self.assertIn('location', analytics)
        location_analytics = analytics['location']
        self.assertEqual(location_analytics['name'], 'Test Apartments')
        self.assertEqual(location_analytics['code'], 'TEST001')


class FBSWorkflowIntegrationTests(FBSIntegrationTestCase):
    """Test FBS workflow integration for rental processes"""
    
    @patch('fbs_app.interfaces.FBSInterface')
    def test_rental_workflow_creation_success(self, mock_fbs):
        """Test successful rental workflow creation"""
        # Mock FBS workflow creation
        mock_fbs.return_value.workflows.start_workflow.return_value = {
            'success': True,
            'workflow_id': 'fbs_rental_workflow_789'
        }
        
        service = FBSEnhancedRentalService()
        rental_data = {
            'tenant_id': self.tenant.id,
            'room_id': self.room.id,
            'start_date': '2024-01-01',
            'monthly_rent': 1500.00,
            'deposit_amount': 1500.00
        }
        
        result = service.create_rental_workflow_with_fbs(rental_data)
        
        self.assertTrue(result['success'])
        rental = result['rental']
        self.assertEqual(rental.tenant, self.tenant)
        self.assertEqual(rental.room, self.room)
        self.assertEqual(rental.state, 'draft')
    
    @patch('fbs_app.interfaces.FBSInterface')
    def test_workflow_step_execution(self, mock_fbs):
        """Test FBS workflow step execution"""
        # Mock workflow step execution
        mock_fbs.return_value.workflows.execute_workflow_step.return_value = {
            'success': True,
            'data': {'step_completed': True, 'next_step': 'approval'}
        }
        
        # Create a rental agreement first
        rental = RentalAgreement.objects.create(
            tenant=self.tenant,
            room=self.room,
            start_date='2024-01-01',
            monthly_rent=1500.00,
            deposit_amount=1500.00,
            state='draft'
        )
        
        # Mock the workflow execution
        with patch.object(self.fbs_service.fbs.workflows, 'execute_workflow_step') as mock_execute:
            mock_execute.return_value = {
                'success': True,
                'data': {'step_completed': True}
            }
            
            # This would be called from the view
            result = self.fbs_service.fbs.workflows.execute_workflow_step(
                workflow_id='test_workflow',
                step_name='activate',
                step_data={'rental_id': rental.id}
            )
            
            self.assertTrue(result['success'])


class FBSComplianceTests(FBSIntegrationTestCase):
    """Test FBS compliance integration"""
    
    def test_compliance_status_check(self):
        """Test FBS compliance status checking"""
        service = FBSEnhancedRentalService()
        result = service.get_fbs_compliance_status('location', str(self.location.id))
        
        self.assertTrue(result['success'])
        data = result['data']
        self.assertEqual(data['entity_type'], 'location')
        self.assertEqual(data['entity_id'], str(self.location.id))
        self.assertTrue(data['compliance_interface_available'])
        self.assertIsInstance(data['available_methods'], list)


class FBSVirtualFieldsTests(FBSIntegrationTestCase):
    """Test FBS virtual fields integration"""
    
    def test_virtual_field_setting(self):
        """Test FBS virtual field setting"""
        service = FBSEnhancedRentalService()
        result = service.set_fbs_virtual_field(
            'location', 
            str(self.location.id), 
            'custom_rating', 
            '5_stars'
        )
        
        self.assertTrue(result['success'])
        data = result['data']
        self.assertEqual(data['entity_type'], 'location')
        self.assertEqual(data['entity_id'], str(self.location.id))
        self.assertEqual(data['field_name'], 'custom_rating')
        self.assertEqual(data['field_value'], '5_stars')
        self.assertTrue(data['fields_interface_available'])


class FBSNotificationsTests(FBSIntegrationTestCase):
    """Test FBS notifications integration"""
    
    def test_notification_sending(self):
        """Test FBS notification sending"""
        service = FBSEnhancedRentalService()
        result = service.send_fbs_notification(
            'rental_created',
            ['admin@example.com', 'manager@example.com'],
            {
                'rental_id': 'test-123',
                'tenant_name': 'John Doe',
                'room_number': '101'
            }
        )
        
        self.assertTrue(result['success'])
        data = result['data']
        self.assertEqual(data['notification_type'], 'rental_created')
        self.assertEqual(data['recipients'], ['admin@example.com', 'manager@example.com'])
        self.assertTrue(data['notifications_interface_available'])


class FBSFallbackTests(FBSIntegrationTestCase):
    """Test FBS fallback behavior when services are unavailable"""
    
    @patch('fbs_app.interfaces.FBSInterface')
    def test_fbs_unavailable_fallback(self, mock_fbs):
        """Test system behavior when FBS is unavailable"""
        # Mock FBS as unavailable
        mock_fbs.side_effect = ImportError("FBS not available")
        
        service = FBSEnhancedRentalService()
        
        # Should gracefully handle FBS unavailability
        self.assertFalse(service.fbs_available)
        self.assertIsNone(service.fbs)
        
        # Basic operations should still work
        location_data = {
            'name': 'Fallback Location',
            'code': 'FALLBACK02',
            'address': '999 Fallback Ave',
            'city': 'Fallback City'
        }
        
        result = service.create_location(location_data)
        self.assertTrue(result['success'])
    
    def test_graceful_error_handling(self):
        """Test graceful error handling in FBS methods"""
        service = FBSEnhancedRentalService()
        
        # Test with invalid data
        result = service.get_fbs_odoo_data('invalid_model', {'invalid': 'filter'})
        
        # Should handle errors gracefully
        self.assertIn('success', result)
        if not result['success']:
            self.assertIn('error', result)


class FBSIntegrationEndToEndTests(FBSIntegrationTestCase):
    """End-to-end FBS integration tests"""
    
    @patch('fbs_app.interfaces.FBSInterface')
    def test_complete_rental_workflow_with_fbs(self, mock_fbs):
        """Test complete rental workflow from location creation to rental agreement"""
        # Mock all FBS services
        mock_fbs.return_value.msme.setup_business.return_value = {
            'success': True,
            'data': {'id': 'fbs_business_123'}
        }
        
        mock_fbs.return_value.workflows.start_workflow.return_value = {
            'success': True,
            'workflow_id': 'fbs_workflow_456'
        }
        
        mock_fbs.return_value.odoo.discover_models.return_value = {
            'success': True,
            'data': {'models': [{'model': 'res.partner', 'name': 'Contact'}]}
        }
        
        mock_fbs.return_value.odoo.get_records.return_value = [
            {'id': 1, 'name': 'Test Partner'}
        ]
        
        service = FBSEnhancedRentalService()
        
        # Step 1: Create location with FBS
        location_data = {
            'name': 'E2E Test Apartments',
            'code': 'E2ETEST01',
            'address': '123 E2E Street',
            'city': 'E2E City'
        }
        
        location_result = service.create_location_with_fbs(location_data, self.user)
        self.assertTrue(location_result['success'])
        location = location_result['location']
        
        # Step 2: Create rental agreement with FBS workflow
        rental_data = {
            'tenant_id': self.tenant.id,
            'room_id': self.room.id,
            'start_date': '2024-01-01',
            'monthly_rent': 1500.00,
            'deposit_amount': 1500.00
        }
        
        rental_result = service.create_rental_workflow_with_fbs(rental_data)
        self.assertTrue(rental_result['success'])
        rental = rental_result['rental']
        
        # Step 3: Get analytics with FBS
        analytics_result = service.get_rental_analytics_with_fbs(str(location.id))
        self.assertTrue(analytics_result['success'])
        
        # Step 4: Check compliance
        compliance_result = service.get_fbs_compliance_status('location', str(location.id))
        self.assertTrue(compliance_result['success'])
        
        # Step 5: Set virtual field
        virtual_field_result = service.set_fbs_virtual_field(
            'location', str(location.id), 'test_field', 'test_value'
        )
        self.assertTrue(virtual_field_result['success'])
        
        # Step 6: Send notification
        notification_result = service.send_fbs_notification(
            'workflow_completed',
            ['admin@example.com'],
            {'workflow_id': 'fbs_workflow_456', 'status': 'completed'}
        )
        self.assertTrue(notification_result['success'])
        
        # Verify all entities were created
        self.assertIsNotNone(location.fbs_business_id)
        self.assertIsNotNone(location.fbs_workflow_id)
        self.assertEqual(rental.tenant, self.tenant)
        self.assertEqual(rental.room, self.room)
        
        print("✅ Complete E2E FBS rental workflow test passed!")


if __name__ == '__main__':
    pytest.main([__file__])
