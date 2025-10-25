# FBS Integration Guide

## Overview

This guide demonstrates how to **embed FBS (Fayvad Business Suite)** into your Django projects to add Odoo-driven business management capabilities. FBS provides service interfaces rather than API endpoints, offering maximum   performance and flexibility.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Your Django Project                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   FBS App       │  │   FBS DMS       │  │   License   │ │
│  │   (Core Suite)  │  │   (Documents)   │  │   Manager   │ │
│  │                 │  │                 │  │             │ │
│  │ • MSME Mgmt     │  │ • Doc Storage   │  │ • Features  │ │
│  │ • BI & Reports  │  │ • Workflows     │  │ • Limits    │ │
│  │ • Workflows     │  │ • Approvals     │  │ • Upgrades  │ │
│  │ • Compliance    │  │ • Odoo Sync     │  │             │ │
│  │ • Accounting    │  │                 │  │             │ │
│  │ • Odoo Int.     │  │                 │  │             │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Odoo ERP      │
                       │ (Primary Data)  │
                       │                 │
                       │ • ir.attachment │
                       │ • res.partner   │
                       │ • res.company   │
                       │ • + Virtual     │
                       │   Fields        │
                       └─────────────────┘
```

## Quick Start

### 1. Initialize FBS Interface

```python
from fbs_app.interfaces import FBSInterface

# Initialize with solution context
fbs = FBSInterface('your_solution_name')

# Check system health
health = fbs.get_system_health()
print(f"FBS Status: {health['status']}")
```

### 2. Access Core Capabilities

```python
# MSME Business Management
dashboard = fbs.msme.get_dashboard()
kpis = fbs.msme.calculate_kpis()

# Business Intelligence
reports = fbs.bi.generate_reports()
charts = fbs.bi.get_charts()

# Workflow Management
workflows = fbs.workflows.get_active_workflows()
approval = fbs.workflows.create_approval_request()

# Odoo Integration
models = fbs.odoo.discover_models()
records = fbs.odoo.get_records('res.partner')
```

## Core Integration Patterns

### 1. Odoo Integration

FBS provides seamless access to Odoo data through the `odoo` interface:

```python
# Discover available models
models = fbs.odoo.discover_models()
print(f"Available Odoo models: {[m['name'] for m in models['data']]}")

# Get records with filters
partners = fbs.odoo.get_records(
    'res.partner',
    filters=[('is_company', '=', True)],
    fields=['name', 'email', 'phone'],
    limit=10
)

# Create new records
new_partner = fbs.odoo.create_record('res.partner', {
    'name': 'New Company',
    'email': 'info@newcompany.com',
    'is_company': True
})

# Update existing records
update_result = fbs.odoo.update_record(
    'res.partner',
    new_partner['data']['id'],
    {'phone': '+1234567890'}
)

# Execute Odoo methods
result = fbs.odoo.execute_method(
    'res.partner',
    'action_view_contacts',
    [new_partner['data']['id']]
)
```

### 2. Virtual Fields (Custom Data)

Extend Odoo models with custom data without modifying Odoo:

```python
# Set custom field
fbs.fields.set_custom_field(
    'res.partner',
    partner_id,
    'loyalty_tier',
    'gold',
    'char'
)

# Get custom field
loyalty = fbs.fields.get_custom_field(
    'res.partner',
    partner_id,
    'loyalty_tier'
)

# Get all custom fields for a record
all_custom = fbs.fields.get_custom_fields(
    'res.partner',
    partner_id
)

# Merge Odoo data with custom fields
complete_record = fbs.fields.merge_odoo_with_custom(
    'res.partner',
    partner_id,
    odoo_fields=['name', 'email', 'phone']
)
```

### 3. MSME Business Management

```python
# Setup new business
business_setup = fbs.msme.setup_business('retail', {
    'business_name': 'My Retail Store',
    'industry': 'retail',
    'location': 'Downtown'
})

# Get business dashboard
dashboard = fbs.msme.get_dashboard()

# Calculate KPIs
kpis = fbs.msme.calculate_kpis()

# Update business profile
profile_update = fbs.msme.update_business_profile({
    'description': 'Updated business description',
    'contact_person': 'John Doe'
})

# Get marketing data
marketing = fbs.msme.get_marketing_data()

# Apply business template
template_result = fbs.msme.apply_business_template('retail_standard')
```

### 4. Business Intelligence

```python
# Create dashboard
dashboard = fbs.bi.create_dashboard({
    'name': 'Sales Dashboard',
    'dashboard_type': 'financial',
    'layout': {'charts': ['sales', 'revenue']}
})

# Create KPI
kpi = fbs.bi.create_kpi({
    'name': 'Monthly Revenue',
    'kpi_type': 'financial',
    'target_value': 50000,
    'calculation_method': 'sum'
})

# Generate report
report = fbs.bi.generate_report(
    report_id=1,
    parameters={'period': 'month', 'year': 2025}
)

# Get analytics data
analytics = fbs.bi.get_analytics_data(
    'sales',
    filters={'period': 'month', 'category': 'electronics'}
)
```

### 5. Workflow Management

```python
# Create workflow definition
workflow_def = fbs.workflows.create_workflow_definition({
    'name': 'Purchase Approval',
    'workflow_type': 'approval',
    'steps': ['request', 'manager_review', 'finance_approval']
})

# Start workflow instance
workflow_instance = fbs.workflows.start_workflow(
    workflow_definition_id=workflow_def['data']['id'],
    initial_data={'amount': 5000, 'purpose': 'Equipment'}
)

# Execute workflow step
step_result = fbs.workflows.execute_workflow_step(
    workflow_instance_id=workflow_instance['data']['id'],
    step_data={'approved': True, 'comments': 'Approved'}
)

# Get active workflows
active_workflows = fbs.workflows.get_active_workflows(user_id=current_user.id)
```

### 6. Document Management (DMS)

```python
from fbs_dms.services import OdooDMSService

# Initialize DMS service
dms = OdooDMSService('your_company_id', fbs)

# Create document
document = dms.create_document({
    'name': 'Business Plan 2025',
    'document_type': 'strategy',
    'category': 'planning',
    'description': 'Annual business strategy document',
    'file_data': file_content
}, user)

# Get document
doc = dms.get_document(document_id=123)

# Update document
update_result = dms.update_document(
    document_id=123,
    update_data={'description': 'Updated description'},
    user=user
)

# Search documents
search_results = dms.search_documents(
    query='business plan',
    filters={'category': 'strategy', 'status': 'active'}
)
```

### 7. License Management

```python
from fbs_license_manager.services import OdooLicenseService

# Initialize license service
license_service = OdooLicenseService('your_company_id', fbs)

# Create license
license = license_service.create_license({
    'company_name': 'New Company Ltd',
    'license_type': 'professional',
    'features': ['msme', 'bi', 'workflows'],
    'expiry_date': '2025-12-31'
}, user)

# Check feature access
access = license_service.check_feature_access('msme_businesses', current_usage=5)

# Update license
update_result = license_service.update_license(
    license_id=123,
    update_data={'features': ['msme', 'bi', 'workflows', 'dms']}
)

# Search licenses
search_results = license_service.search_licenses(
    filters={'license_type': 'professional', 'status': 'active'}
)
```

## Advanced Integration Patterns

### 1. Multi-Solution Architecture

```python
# Initialize multiple solutions
retail_fbs = FBSInterface('retail_solution')
manufacturing_fbs = FBSInterface('manufacturing_solution')

# Each solution has isolated data
retail_partners = retail_fbs.odoo.get_records('res.partner')
manufacturing_partners = manufacturing_fbs.odoo.get_records('res.partner')

# Solutions can share the same Odoo instance but with different databases
```

### 2. Custom Service Wrappers

```python
class BusinessService:
    def __init__(self, solution_name):
        self.fbs = FBSInterface(solution_name)
    
    def get_customer_summary(self, customer_id):
        """Get comprehensive customer information"""
        # Get Odoo data
        customer = self.fbs.odoo.get_record('res.partner', customer_id)
        
        # Get custom fields
        custom_data = self.fbs.fields.get_custom_fields('res.partner', customer_id)
        
        # Get related documents
        documents = self.fbs.odoo.get_records(
            'ir.attachment',
            filters=[('res_model', '=', 'res.partner'), ('res_id', '=', customer_id)]
        )
        
        return {
            'customer': customer['data'],
            'custom_fields': custom_data['data'],
            'documents': documents['data']
        }
    
    def create_customer_with_documents(self, customer_data, documents):
        """Create customer and attach documents"""
        # Create customer in Odoo
        customer = self.fbs.odoo.create_record('res.partner', customer_data)
        
        # Add custom fields
        if customer_data.get('loyalty_tier'):
            self.fbs.fields.set_custom_field(
                'res.partner',
                customer['data']['id'],
                'loyalty_tier',
                customer_data['loyalty_tier']
            )
        
        # Attach documents
        for doc in documents:
            self.fbs.odoo.create_record('ir.attachment', {
                'name': doc['name'],
                'res_model': 'res.partner',
                'res_id': customer['data']['id'],
                'datas': doc['content']
            })
        
        return customer

# Usage
business_service = BusinessService('retail_solution')
customer_summary = business_service.get_customer_summary(123)
```

### 3. Event-Driven Integration

```python
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=YourModel)
def sync_with_odoo(sender, instance, created, **kwargs):
    """Sync Django model changes with Odoo"""
    fbs = FBSInterface('your_solution')
    
    if created:
        # Create in Odoo
        odoo_record = fbs.odoo.create_record('your.odoo.model', {
            'name': instance.name,
            'description': instance.description
        })
        
        # Store Odoo ID reference
        instance.odoo_id = odoo_record['data']['id']
        instance.save(update_fields=['odoo_id'])
    else:
        # Update in Odoo
        if instance.odoo_id:
            fbs.odoo.update_record('your.odoo.model', instance.odoo_id, {
                'name': instance.name,
                'description': instance.description
            })
```

### 4. Caching and Performance

```python
# Use FBS cache for performance
fbs.cache.set_cache('customer_123', customer_data, expiry_hours=24)

# Get cached data
cached_customer = fbs.cache.get_cache('customer_123')

# Clear cache when needed
fbs.cache.delete_cache('customer_123')

# Get cache statistics
cache_stats = fbs.cache.get_cache_stats()
```

## Error Handling

### 1. Service-Level Error Handling

```python
def safe_odoo_operation(operation_func, *args, **kwargs):
    """Safely execute Odoo operations with error handling"""
    try:
        result = operation_func(*args, **kwargs)
        
        if not result.get('success'):
            logger.error(f"Odoo operation failed: {result.get('error')}")
            return {
                'success': False,
                'error': result.get('error'),
                'fallback_data': get_fallback_data()
            }
        
        return result
        
    except Exception as e:
        logger.error(f"Odoo operation exception: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'fallback_data': get_fallback_data()
        }

# Usage
partners = safe_odoo_operation(
    fbs.odoo.get_records,
    'res.partner',
    limit=10
)
```

### 2. Graceful Degradation

```python
def get_business_data(solution_name):
    """Get business data with graceful degradation"""
    fbs = FBSInterface(solution_name)
    
    # Try to get from Odoo first
    try:
        if fbs.is_odoo_available():
            return fbs.msme.get_dashboard()
    except Exception as e:
        logger.warning(f"Odoo unavailable: {str(e)}")
    
    # Fallback to Django models
    try:
        from your_app.models import BusinessData
        return BusinessData.objects.filter(solution=solution_name).first()
    except Exception as e:
        logger.error(f"Django fallback failed: {str(e)}")
        return get_default_data()
```

## Testing Integration

### 1. Unit Tests

```python
from django.test import TestCase
from unittest.mock import patch, MagicMock

class FBSIntegrationTest(TestCase):
    def setUp(self):
        self.fbs = FBSInterface('test_solution')
    
    @patch('fbs_app.interfaces.FBSInterface')
    def test_odoo_integration(self, mock_fbs):
        # Mock Odoo responses
        mock_fbs.odoo.get_records.return_value = {
            'success': True,
            'data': [{'id': 1, 'name': 'Test Partner'}]
        }
        
        # Test integration
        result = mock_fbs.odoo.get_records('res.partner')
        self.assertTrue(result['success'])
        self.assertEqual(len(result['data']), 1)
```

### 2. Integration Tests

```python
class FBSIntegrationTestCase(TestCase):
    def setUp(self):
        # Setup test database
        self.solution_name = 'test_solution'
        self.fbs = FBSInterface(self.solution_name)
    
    def test_full_workflow(self):
        """Test complete business workflow"""
        # Create customer
        customer = self.fbs.odoo.create_record('res.partner', {
            'name': 'Test Customer',
            'is_company': True
        })
        
        # Add custom field
        self.fbs.fields.set_custom_field(
            'res.partner',
            customer['data']['id'],
            'customer_type',
            'premium'
        )
        
        # Create document
        from fbs_dms.services import OdooDMSService
        dms = OdooDMSService(self.solution_name, self.fbs)
        
        document = dms.create_document({
            'name': 'Test Document',
            'document_type': 'contract'
        }, self.user)
        
        # Verify integration
        self.assertTrue(customer['success'])
        self.assertTrue(document['success'])
```

## Performance Considerations

### 1. Batch Operations

```python
def batch_create_partners(partner_data_list):
    """Create multiple partners efficiently"""
    results = []
    
    for partner_data in partner_data_list:
        result = fbs.odoo.create_record('res.partner', partner_data)
        results.append(result)
        
        # Add custom fields in batch
        if result['success'] and partner_data.get('custom_fields'):
            for field_name, field_value in partner_data['custom_fields'].items():
                fbs.fields.set_custom_field(
                    'res.partner',
                    result['data']['id'],
                    field_name,
                    field_value
                )
    
    return results
```

### 2. Caching Strategy

```python
def get_cached_partner(partner_id):
    """Get partner with intelligent caching"""
    cache_key = f'partner_{partner_id}'
    
    # Try cache first
    cached = fbs.cache.get_cache(cache_key)
    if cached:
        return cached['data']
    
    # Get from Odoo
    partner = fbs.odoo.get_record('res.partner', partner_id)
    
    if partner['success']:
        # Cache for 1 hour
        fbs.cache.set_cache(cache_key, partner['data'], expiry_hours=1)
        return partner['data']
    
    return None
```

## Best Practices

### 1. Solution Isolation

- Always use unique solution names for different deployments
- Keep solution-specific data separate
- Use appropriate database routing

### 2. Error Handling

- Implement comprehensive error handling
- Provide meaningful error messages
- Use fallback mechanisms when possible

### 3. Performance

- Cache frequently accessed data
- Use batch operations for bulk data
- Monitor Odoo response times

### 4. Security

- Validate all input data
- Use appropriate authentication
- Implement proper access controls

## Next Steps

1. **Read the [Developer Guide](DEVELOPER_GUIDE.md)** - Deep dive into service interfaces
2. **Check [Odoo Integration](ODOO_INTEGRATION.md)** - Master Odoo + Virtual Fields
3. **Explore [API Reference](API_REFERENCE.md)** - Complete interface documentation
4. **Review examples** - Study the provided code examples

---

**FBS Integration Complete!** 🚀

Your Django project now has access to enterprise-grade business management capabilities through FBS Virtual Fields technology.
