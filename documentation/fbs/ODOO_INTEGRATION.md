# FBS Odoo Integration Guide

## Overview

This guide covers the **Odoo-driven architecture** of FBS, where Odoo ERP serves as the primary data store and FBS Virtual Fields extend Odoo models with custom data. This approach provides the best of both worlds: enterprise ERP capabilities with flexible customizations.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    FBS Interface Layer                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   Odoo Client   │  │  Virtual Fields │  │   Services  │ │
│  │                 │  │                 │  │             │ │
│  │ • XML-RPC       │  │ • Custom Data   │  │ • MSME      │ │
│  │ • Model Disc.   │  │ • Field Merging │  │ • BI        │ │
│  │ • CRUD Ops      │  │ • Extensions    │  │ • Workflows │ │
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

## Core Concepts

### 1. **Odoo as Primary Data Store**
- **Documents**: Stored in `ir.attachment` model
- **Companies/Licenses**: Stored in `res.partner` model
- **Business Data**: Stored in standard Odoo models
- **Custom Extensions**: Added via FBS Virtual Fields

### 2. **FBS Virtual Fields**
- Extend Odoo models without modification
- Store custom data in solution-specific databases
- Seamlessly merge with Odoo data
- Support multiple data types (char, text, date, numeric, JSON)

### 3. **Hybrid Data Model**
- Odoo provides core business data
- FBS Virtual Fields add custom functionality
- Django models serve as UI references
- Real-time synchronization between systems

## Odoo Integration Interface

### **Basic Usage**

```python
from fbs_app.interfaces import FBSInterface

# Initialize interface
fbs = FBSInterface('your_solution_name')

# Access Odoo integration
odoo = fbs.odoo
```

### **Model Discovery**

```python
# Discover available Odoo models
models = fbs.odoo.discover_models()
print(f"Available models: {[m['name'] for m in models['data']]}")

# Discover fields for a specific model
fields = fbs.odoo.discover_fields('res.partner')
print(f"Partner fields: {[f['name'] for f in fields['data']]}")

# Discover installed modules
modules = fbs.odoo.discover_modules()
print(f"Installed modules: {[m['name'] for m in modules['data']]}")
```

### **CRUD Operations**

```python
# Create record
new_partner = fbs.odoo.create_record('res.partner', {
    'name': 'New Company Ltd',
    'email': 'info@newcompany.com',
    'is_company': True,
    'customer_rank': 1
})

# Read record
partner = fbs.odoo.get_record('res.partner', new_partner['data']['id'])

# Update record
update_result = fbs.odoo.update_record('res.partner', partner_id, {
    'phone': '+1234567890',
    'website': 'https://newcompany.com'
})

# Delete record
delete_result = fbs.odoo.delete_record('res.partner', partner_id)

# List records with filters
partners = fbs.odoo.get_records(
    'res.partner',
    filters=[('is_company', '=', True), ('active', '=', True)],
    fields=['name', 'email', 'phone'],
    limit=50
)
```

### **Method Execution**

```python
# Execute Odoo model methods
result = fbs.odoo.execute_method(
    'res.partner',
    'action_view_contacts',
    [partner_id]
)

# Execute with parameters
result = fbs.odoo.execute_method(
    'sale.order',
    'action_confirm',
    [order_id],
    parameters={'context': {'skip_validation': True}}
)
```

## Virtual Fields Integration

### **Setting Custom Fields**

```python
# Set simple text field
fbs.fields.set_custom_field(
    'res.partner',
    partner_id,
    'loyalty_tier',
    'gold',
    'char'
)

# Set complex data (JSON)
fbs.fields.set_custom_field(
    'res.partner',
    partner_id,
    'preferences',
    {'theme': 'dark', 'notifications': True, 'language': 'en'},
    'json'
)

# Set date field
fbs.fields.set_custom_field(
    'res.partner',
    partner_id,
    'contract_start',
    '2025-01-01',
    'date'
)

# Set numeric field
fbs.fields.set_custom_field(
    'res.partner',
    partner_id,
    'credit_limit',
    50000.00,
    'numeric'
)
```

### **Retrieving Custom Fields**

```python
# Get specific custom field
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

# Get custom fields for multiple records
custom_fields = fbs.fields.get_custom_fields(
    'res.partner',
    partner_id,
    field_names=['loyalty_tier', 'preferences', 'credit_limit']
)
```

### **Merging Odoo and Custom Data**

```python
# Get complete record with custom fields
complete_record = fbs.fields.merge_odoo_with_custom(
    'res.partner',
    partner_id,
    odoo_fields=['name', 'email', 'phone', 'is_company']
)

# Result structure:
# {
#     'success': True,
#     'data': {
#         'odoo_data': {
#             'id': 123,
#             'name': 'Company Name',
#             'email': 'info@company.com',
#             'phone': '+1234567890',
#             'is_company': True
#         },
#         'custom_fields': {
#             'loyalty_tier': 'gold',
#             'preferences': {'theme': 'dark', 'notifications': True},
#             'credit_limit': 50000.00
#         },
#         'merged_data': {
#             'id': 123,
#             'name': 'Company Name',
#             'email': 'info@company.com',
#             'phone': '+1234567890',
#             'is_company': True,
#             'loyalty_tier': 'gold',
#             'preferences': {'theme': 'dark', 'notifications': True},
#             'credit_limit': 50000.00
#         }
#     }
# }
```

## Document Management Integration

### **Storing Documents in Odoo**

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
    'file_data': file_content,
    'metadata': {
        'department': 'Strategy',
        'priority': 'high',
        'review_date': '2025-06-01'
    }
}, user)
```

### **Document Operations**

```python
# Get document
doc = dms.get_document(document_id=123)

# Update document
update_result = dms.update_document(
    document_id=123,
    update_data={
        'description': 'Updated description',
        'metadata': {'priority': 'urgent'}
    },
    user=user
)

# Search documents
search_results = dms.search_documents(
    query='business plan',
    filters={
        'category': 'strategy',
        'status': 'active',
        'created_after': '2025-01-01'
    }
)

# Delete document
delete_result = dms.delete_document(document_id=123, user=user)
```

## License Management Integration

### **Storing Licenses in Odoo**

```python
from fbs_license_manager.services import OdooLicenseService

# Initialize license service
license_service = OdooLicenseService('your_company_id', fbs)

# Create license
license = license_service.create_license({
    'company_name': 'New Company Ltd',
    'license_type': 'professional',
    'features': ['msme', 'bi', 'workflows', 'dms'],
    'expiry_date': '2025-12-31',
    'max_users': 25,
    'max_storage_gb': 100
}, user)
```

### **License Operations**

```python
# Get license
license_info = license_service.get_license(license_id=123)

# Update license
update_result = license_service.update_license(
    license_id=123,
    update_data={
        'features': ['msme', 'bi', 'workflows', 'dms', 'advanced_analytics'],
        'max_users': 50
    }
)

# Check feature access
access = license_service.check_feature_access(
    'msme_businesses',
    current_usage=5
)

# Search licenses
search_results = license_service.search_licenses(
    filters={
        'license_type': 'professional',
        'status': 'active',
        'expires_after': '2025-06-01'
    }
)
```

## Advanced Integration Patterns

### 1. **Multi-Model Relationships**

```python
def create_customer_with_documents(customer_data, documents):
    """Create customer and attach multiple documents"""
    try:
        # 1. Create customer in Odoo
        customer = fbs.odoo.create_record('res.partner', {
            'name': customer_data['name'],
            'email': customer_data['email'],
            'is_company': True,
            'customer_rank': 1
        })
        
        if not customer['success']:
            return customer
        
        customer_id = customer['data']['id']
        
        # 2. Add custom fields
        if customer_data.get('loyalty_tier'):
            fbs.fields.set_custom_field(
                'res.partner',
                customer_id,
                'loyalty_tier',
                customer_data['loyalty_tier']
            )
        
        # 3. Attach documents
        attached_docs = []
        for doc in documents:
            doc_result = fbs.odoo.create_record('ir.attachment', {
                'name': doc['name'],
                'res_model': 'res.partner',
                'res_id': customer_id,
                'datas': doc['content'],
                'mimetype': doc.get('mimetype', 'application/octet-stream')
            })
            
            if doc_result['success']:
                # Add document metadata as custom fields
                fbs.fields.set_custom_field(
                    'ir.attachment',
                    doc_result['data']['id'],
                    'document_category',
                    doc.get('category', 'general')
                )
                
                attached_docs.append(doc_result['data']['id'])
        
        return {
            'success': True,
            'customer_id': customer_id,
            'attached_documents': attached_docs,
            'message': 'Customer created with documents successfully'
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}
```

### 2. **Data Synchronization**

```python
def sync_odoo_with_django(odoo_model, django_model, sync_fields):
    """Synchronize Odoo data with Django models"""
    try:
        # Get all Odoo records
        odoo_records = fbs.odoo.get_records(odoo_model, limit=1000)
        
        if not odoo_records['success']:
            return odoo_records
        
        synced_count = 0
        for odoo_record in odoo_records['data']:
            # Check if Django record exists
            django_record = django_model.objects.filter(
                odoo_id=odoo_record['id']
            ).first()
            
            if django_record:
                # Update existing record
                for field in sync_fields:
                    if field in odoo_record:
                        setattr(django_record, field, odoo_record[field])
                django_record.save()
            else:
                # Create new Django record
                django_data = {
                    'odoo_id': odoo_record['id']
                }
                for field in sync_fields:
                    if field in odoo_record:
                        django_data[field] = odoo_record[field]
                
                django_model.objects.create(**django_data)
            
            synced_count += 1
        
        return {
            'success': True,
            'synced_count': synced_count,
            'message': f'Synchronized {synced_count} records'
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}
```

### 3. **Real-Time Updates**

```python
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=YourModel)
def sync_with_odoo(sender, instance, created, **kwargs):
    """Sync Django model changes with Odoo in real-time"""
    try:
        if created:
            # Create in Odoo
            odoo_data = {
                'name': instance.name,
                'description': instance.description,
                # Map other fields
            }
            
            odoo_record = fbs.odoo.create_record('your.odoo.model', odoo_data)
            
            if odoo_record['success']:
                # Store Odoo ID reference
                instance.odoo_id = odoo_record['data']['id']
                instance.save(update_fields=['odoo_id'])
                
                # Add custom fields
                if instance.custom_field:
                    fbs.fields.set_custom_field(
                        'your.odoo.model',
                        instance.odoo_id,
                        'custom_field',
                        instance.custom_field
                    )
        else:
            # Update in Odoo
            if instance.odoo_id:
                update_data = {
                    'name': instance.name,
                    'description': instance.description,
                    # Map other fields
                }
                
                fbs.odoo.update_record('your.odoo.model', instance.odoo_id, update_data)
                
                # Update custom fields
                if instance.custom_field:
                    fbs.fields.set_custom_field(
                        'your.odoo.model',
                        instance.odoo_id,
                        'custom_field',
                        instance.custom_field
                    )
                    
    except Exception as e:
        logger.error(f"Failed to sync with Odoo: {str(e)}")
```

## Performance Optimization

### 1. **Batch Operations**

```python
def batch_create_with_custom_fields(model_name, records_data):
    """Create multiple records with custom fields efficiently"""
    results = []
    
    for record_data in records_data:
        # Create base record
        result = fbs.odoo.create_record(model_name, record_data['odoo_data'])
        
        if result['success']:
            record_id = result['data']['id']
            
            # Add custom fields in batch
            custom_fields = record_data.get('custom_fields', {})
            for field_name, field_value in custom_fields.items():
                fbs.fields.set_custom_field(
                    model_name,
                    record_id,
                    field_name,
                    field_value
                )
            
            results.append({
                'success': True,
                'id': record_id,
                'original_data': record_data
            })
        else:
            results.append({
                'success': False,
                'error': result.get('error'),
                'original_data': record_data
            })
    
    return results
```

### 2. **Caching Strategy**

```python
def get_cached_odoo_data(cache_key, fetch_func, *args, **kwargs):
    """Get Odoo data with intelligent caching"""
    # Try cache first
    cached = fbs.cache.get_cache(cache_key)
    if cached:
        return cached['data']
    
    # Fetch from Odoo
    result = fetch_func(*args, **kwargs)
    
    if result['success']:
        # Cache for 1 hour
        fbs.cache.set_cache(cache_key, result['data'], expiry_hours=1)
        return result['data']
    
    return None

# Usage
partners = get_cached_odoo_data(
    'partners_active',
    fbs.odoo.get_records,
    'res.partner',
    filters=[('active', '=', True)]
)
```

## Error Handling

### 1. **Connection Issues**

```python
def robust_odoo_operation(operation_func, *args, **kwargs):
    """Execute Odoo operations with robust error handling"""
    try:
        # Check Odoo availability
        if not fbs.is_odoo_available():
            return {
                'success': False,
                'error': 'Odoo connection unavailable',
                'fallback_available': True
            }
        
        # Execute operation
        result = operation_func(*args, **kwargs)
        
        if not result.get('success'):
            return {
                'success': False,
                'error': result.get('error'),
                'operation': operation_func.__name__
            }
        
        return result
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'operation': operation_func.__name__,
            'exception_type': type(e).__name__
        }
```

### 2. **Fallback Mechanisms**

```python
def get_data_with_fallback(odoo_operation, django_fallback, *args, **kwargs):
    """Get data with Odoo fallback to Django"""
    try:
        # Try Odoo first
        result = odoo_operation(*args, **kwargs)
        
        if result['success']:
            return result
        
        # Fallback to Django
        logger.warning(f"Odoo operation failed: {result.get('error')}, using Django fallback")
        return django_fallback(*args, **kwargs)
        
    except Exception as e:
        logger.error(f"Both Odoo and Django fallback failed: {str(e)}")
        return {
            'success': False,
            'error': f'All data sources failed: {str(e)}',
            'fallback_used': True
        }
```

## Testing Odoo Integration

### 1. **Mock Testing**

```python
from unittest.mock import patch, MagicMock

class OdooIntegrationTest(TestCase):
    def setUp(self):
        self.fbs = FBSInterface('test_solution')
    
    @patch('fbs_app.interfaces.FBSInterface')
    def test_odoo_operations(self, mock_fbs):
        # Mock Odoo responses
        mock_fbs.odoo.create_record.return_value = {
            'success': True,
            'data': {'id': 123, 'name': 'Test Company'}
        }
        
        mock_fbs.odoo.get_record.return_value = {
            'success': True,
            'data': {'id': 123, 'name': 'Test Company'}
        }
        
        # Test operations
        create_result = mock_fbs.odoo.create_record('res.partner', {'name': 'Test'})
        self.assertTrue(create_result['success'])
        
        get_result = mock_fbs.odoo.get_record('res.partner', 123)
        self.assertTrue(get_result['success'])
```

### 2. **Integration Testing**

```python
class OdooIntegrationTestCase(TestCase):
    def setUp(self):
        self.solution_name = 'test_solution'
        self.fbs = FBSInterface(self.solution_name)
    
    def test_full_odoo_workflow(self):
        """Test complete Odoo integration workflow"""
        # Create record
        partner = self.fbs.odoo.create_record('res.partner', {
            'name': 'Test Partner',
            'is_company': True
        })
        
        self.assertTrue(partner['success'])
        partner_id = partner['data']['id']
        
        # Add custom field
        field_result = self.fbs.fields.set_custom_field(
            'res.partner',
            partner_id,
            'test_field',
            'test_value'
        )
        
        self.assertTrue(field_result['success'])
        
        # Get complete record
        complete = self.fbs.fields.merge_odoo_with_custom(
            'res.partner',
            partner_id,
            odoo_fields=['name', 'is_company']
        )
        
        self.assertTrue(complete['success'])
        self.assertIn('test_field', complete['data']['custom_fields'])
```

## Best Practices

### 1. **Data Consistency**
- Always check operation success status
- Implement proper error handling
- Use transactions for multi-step operations
- Validate data before sending to Odoo

### 2. **Performance**
- Cache frequently accessed data
- Use batch operations for bulk data
- Monitor Odoo response times
- Implement connection pooling

### 3. **Security**
- Validate all input data
- Use appropriate authentication
- Implement proper access controls
- Sanitize error messages

### 4. **Maintenance**
- Monitor Odoo connectivity
- Implement health checks
- Use comprehensive logging
- Plan for Odoo upgrades

## Troubleshooting

### **Common Issues**

#### 1. **Connection Timeouts**
```python
# Check Odoo availability
if not fbs.is_odoo_available():
    print("Odoo connection timeout - check server status")
```

#### 2. **Authentication Errors**
```python
# Verify credentials
try:
    test_connection = fbs.odoo.get_database_info()
    print("Authentication successful")
except Exception as e:
    print(f"Authentication failed: {str(e)}")
```

#### 3. **Model Not Found**
```python
# Discover available models
models = fbs.odoo.discover_models()
available_models = [m['name'] for m in models['data']]
print(f"Available models: {available_models}")
```

## Next Steps

1. **Read the [Developer Guide](DEVELOPER_GUIDE.md)** - Deep dive into service interfaces
2. **Check [Integration Guide](INTEGRATION.md)** - Learn embedding patterns
3. **Explore [API Reference](API_REFERENCE.md)** - Complete interface documentation
4. **Start building** - Begin implementing Odoo integration

---

**Odoo Integration Mastered!** 🚀

You now understand how FBS uses Odoo as the primary data store with Virtual Fields for customizations. Build powerful business applications with enterprise ERP capabilities.
