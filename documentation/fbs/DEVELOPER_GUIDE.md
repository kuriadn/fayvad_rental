# FBS Developer Guide

## Overview

This guide provides developers with comprehensive information about the **FBS (Fayvad Business Suite)** architecture, service interfaces, and development patterns. FBS is built on an Odoo-driven architecture with Django serving as the UI layer.

## Architecture Principles

### 1. **Odoo as Primary Data Store**
- Odoo ERP serves as the main data repository
- Django models act as UI references and business logic containers
- FBS Virtual Fields extend Odoo models without modification

### 2. **Service-Oriented Design**
- Business logic encapsulated in service classes
- Clean interfaces for accessing capabilities
- Separation of concerns between data, business logic, and presentation

### 3. **Multi-Tenant Architecture**
- Solution-based isolation
- Dynamic database routing
- Isolated caching and configuration

## Core Components

### 1. **FBSInterface** - Main Entry Point

The `FBSInterface` is the primary interface for accessing all FBS capabilities:

```python
from fbs_app.interfaces import FBSInterface

# Initialize with solution context
fbs = FBSInterface('your_solution_name')

# Access all capabilities
fbs.odoo          # Odoo integration
fbs.fields        # Virtual fields
fbs.msme          # MSME management
fbs.bi            # Business intelligence
fbs.workflows     # Workflow management
fbs.accounting    # Accounting operations
fbs.cache         # Caching system
```

### 2. **Service Layer Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│                    FBSInterface                            │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   OdooClient    │  │  VirtualFields  │  │   Services  │ │
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
                       └─────────────────┘
```

## Service Interfaces Deep Dive

### 1. **OdooIntegrationInterface**

Provides complete access to Odoo ERP functionality:

```python
class OdooIntegrationInterface:
    """Interface for Odoo ERP Integration operations"""
    
    def discover_models(self, database_name: Optional[str] = None) -> Dict[str, Any]:
        """Discover available Odoo models"""
        
    def discover_fields(self, model_name: str, database_name: Optional[str] = None) -> Dict[str, Any]:
        """Discover fields for a specific model"""
        
    def get_records(self, model_name: str, filters: Optional[Dict[str, Any]] = None, 
                   fields: Optional[List[str]] = None, limit: Optional[int] = None) -> Dict[str, Any]:
        """Get records from Odoo with filtering"""
        
    def create_record(self, model_name: str, record_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new record in Odoo"""
        
    def update_record(self, model_name: str, record_id: int, record_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing record in Odoo"""
        
    def delete_record(self, model_name: str, record_id: int) -> Dict[str, Any]:
        """Delete record from Odoo"""
        
    def execute_method(self, model_name: str, method_name: str, record_ids: List[int], 
                      parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute Odoo model methods"""
```

**Usage Examples:**

```python
# Discover available models
models = fbs.odoo.discover_models()
print(f"Available models: {[m['name'] for m in models['data']]}")

# Get partners with filters
partners = fbs.odoo.get_records(
    'res.partner',
    filters=[('is_company', '=', True), ('active', '=', True)],
    fields=['name', 'email', 'phone'],
    limit=50
)

# Create new partner
new_partner = fbs.odoo.create_record('res.partner', {
    'name': 'New Company Ltd',
    'email': 'info@newcompany.com',
    'is_company': True,
    'customer_rank': 1
})

# Update partner
update_result = fbs.odoo.update_record(
    'res.partner',
    new_partner['data']['id'],
    {'phone': '+1234567890', 'website': 'https://newcompany.com'}
)

# Execute Odoo method
result = fbs.odoo.execute_method(
    'res.partner',
    'action_view_contacts',
    [new_partner['data']['id']]
)
```

### 2. **VirtualFieldsInterface**

Manages custom data extensions to Odoo models:

```python
class VirtualFieldsInterface:
    """Interface for Virtual Fields and Custom Data operations"""
    
    def set_custom_field(self, model_name: str, record_id: int, field_name: str, 
                        field_value: Any, field_type: str = 'char', 
                        database_name: Optional[str] = None) -> Dict[str, Any]:
        """Set custom field value"""
        
    def get_custom_field(self, model_name: str, record_id: int, field_name: str,
                        database_name: Optional[str] = None) -> Dict[str, Any]:
        """Get custom field value"""
        
    def get_custom_fields(self, model_name: str, record_id: int,
                         database_name: Optional[str] = None) -> Dict[str, Any]:
        """Get all custom fields for a record"""
        
    def delete_custom_field(self, model_name: str, record_id: int, field_name: str,
                           database_name: Optional[str] = None) -> Dict[str, Any]:
        """Delete custom field"""
        
    def merge_odoo_with_custom(self, model_name: str, record_id: int,
                              odoo_fields: Optional[List[str]] = None,
                              database_name: Optional[str] = None) -> Dict[str, Any]:
        """Merge Odoo data with custom fields"""
        
    def get_virtual_model_schema(self, model_name: str, 
                                database_name: Optional[str] = None) -> Dict[str, Any]:
        """Get virtual model schema including custom fields"""
```

**Usage Examples:**

```python
# Set custom field
result = fbs.fields.set_custom_field(
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

# Get all custom fields
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

# Get virtual model schema
schema = fbs.fields.get_virtual_model_schema('res.partner')
```

### 3. **MSMEInterface**

Manages MSME-specific business operations:

```python
class MSMEInterface:
    """Interface for MSME-specific operations"""
    
    def setup_business(self, business_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Setup MSME business"""
        
    def get_dashboard(self) -> Dict[str, Any]:
        """Get MSME dashboard data"""
        
    def calculate_kpis(self) -> Dict[str, Any]:
        """Calculate MSME KPIs"""
        
    def get_compliance_status(self) -> Dict[str, Any]:
        """Get compliance status"""
        
    def update_business_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update business profile"""
        
    def get_marketing_data(self) -> Dict[str, Any]:
        """Get marketing data"""
        
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get analytics summary"""
        
    def create_custom_field(self, field_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create custom field"""
        
    def get_business_templates(self) -> Dict[str, Any]:
        """Get business templates"""
        
    def apply_business_template(self, template_name: str) -> Dict[str, Any]:
        """Apply business template"""
```

**Usage Examples:**

```python
# Setup new business
business_setup = fbs.msme.setup_business('retail', {
    'business_name': 'My Retail Store',
    'industry': 'retail',
    'location': 'Downtown',
    'employee_count': 25,
    'annual_revenue': 500000
})

# Get business dashboard
dashboard = fbs.msme.get_dashboard()

# Calculate KPIs
kpis = fbs.msme.calculate_kpis()

# Update business profile
profile_update = fbs.msme.update_business_profile({
    'description': 'Updated business description',
    'contact_person': 'John Doe',
    'phone': '+1234567890'
})

# Get marketing insights
marketing = fbs.msme.get_marketing_data()

# Apply industry template
template_result = fbs.msme.apply_business_template('retail_standard')
```

### 4. **BusinessIntelligenceInterface**

Manages BI, analytics, and reporting:

```python
class BusinessIntelligenceInterface:
    """Interface for Business Intelligence and Analytics operations"""
    
    def create_dashboard(self, dashboard_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new dashboard"""
        
    def get_dashboards(self, dashboard_type: Optional[str] = None) -> Dict[str, Any]:
        """Get all dashboards or by type"""
        
    def update_dashboard(self, dashboard_id: int, dashboard_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update dashboard"""
        
    def delete_dashboard(self, dashboard_id: int) -> Dict[str, Any]:
        """Delete dashboard"""
        
    def create_report(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new report"""
        
    def get_reports(self, report_type: Optional[str] = None) -> Dict[str, Any]:
        """Get all reports or by type"""
        
    def generate_report(self, report_id: int, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate report with parameters"""
        
    def create_kpi(self, kpi_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new KPI"""
        
    def get_kpis(self, kpi_type: Optional[str] = None) -> Dict[str, Any]:
        """Get all KPIs or by type"""
        
    def calculate_kpi(self, kpi_id: int) -> Dict[str, Any]:
        """Calculate KPI value"""
        
    def create_chart(self, chart_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new chart"""
        
    def get_charts(self, chart_type: Optional[str] = None) -> Dict[str, Any]:
        """Get all charts or by type"""
        
    def get_analytics_data(self, data_source: str, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get analytics data from various sources"""
```

**Usage Examples:**

```python
# Create dashboard
dashboard = fbs.bi.create_dashboard({
    'name': 'Sales Dashboard',
    'dashboard_type': 'financial',
    'layout': {
        'charts': ['monthly_sales', 'revenue_trend', 'top_products'],
        'kpis': ['total_sales', 'growth_rate', 'customer_count']
    },
    'refresh_interval': 300  # 5 minutes
})

# Create KPI
kpi = fbs.bi.create_kpi({
    'name': 'Monthly Revenue',
    'kpi_type': 'financial',
    'target_value': 50000,
    'calculation_method': 'sum',
    'data_source': 'sales_data',
    'refresh_interval': 3600  # 1 hour
})

# Generate report
report = fbs.bi.generate_report(
    report_id=1,
    parameters={
        'period': 'month',
        'year': 2025,
        'format': 'pdf',
        'include_charts': True
    }
)

# Get analytics data
analytics = fbs.bi.get_analytics_data(
    'sales',
    filters={
        'period': 'month',
        'category': 'electronics',
        'region': 'north_america'
    }
)
```

### 5. **WorkflowInterface**

Manages business workflows and approvals:

```python
class WorkflowInterface:
    """Interface for Workflow Management operations"""
    
    def create_workflow_definition(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new workflow definition"""
        
    def get_workflow_definitions(self, workflow_type: Optional[str] = None) -> Dict[str, Any]:
        """Get all workflow definitions or by type"""
        
    def start_workflow(self, workflow_definition_id: int, initial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Start a new workflow instance"""
        
    def get_active_workflows(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Get active workflow instances"""
        
    def execute_workflow_step(self, workflow_instance_id: int, step_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a workflow step"""
        
    def create_approval_request(self, approval_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create an approval request"""
```

**Usage Examples:**

```python
# Create workflow definition
workflow_def = fbs.workflows.create_workflow_definition({
    'name': 'Purchase Approval',
    'workflow_type': 'approval',
    'description': 'Multi-level purchase approval workflow',
    'steps': [
        {
            'name': 'request',
            'type': 'input',
            'required_fields': ['amount', 'purpose', 'vendor']
        },
        {
            'name': 'manager_review',
            'type': 'approval',
            'approver_role': 'manager',
            'timeout_hours': 24
        },
        {
            'name': 'finance_approval',
            'type': 'approval',
            'approver_role': 'finance',
            'conditional': True,
            'condition': 'amount > 10000'
        }
    ],
    'transitions': [
        {'from': 'request', 'to': 'manager_review', 'condition': 'always'},
        {'from': 'manager_review', 'to': 'finance_approval', 'condition': 'approved'},
        {'from': 'finance_approval', 'to': 'completed', 'condition': 'approved'}
    ]
})

# Start workflow instance
workflow_instance = fbs.workflows.start_workflow(
    workflow_definition_id=workflow_def['data']['id'],
    initial_data={
        'amount': 15000,
        'purpose': 'Office Equipment',
        'vendor': 'Office Supplies Co',
        'requestor': 'john.doe@company.com'
    }
)

# Execute workflow step
step_result = fbs.workflows.execute_workflow_step(
    workflow_instance_id=workflow_instance['data']['id'],
    step_data={
        'step_name': 'manager_review',
        'approved': True,
        'comments': 'Approved - within budget',
        'approver': 'manager@company.com'
    }
)

# Get active workflows for user
active_workflows = fbs.workflows.get_active_workflows(user_id=current_user.id)
```

### 6. **AccountingInterface**

Manages financial operations and accounting:

```python
class AccountingInterface:
    """Interface for accounting operations"""
    
    def create_cash_entry(self, entry_type: str, amount: float, description: str, 
                         category: str = '', date: Optional[str] = None) -> Dict[str, Any]:
        """Create cash basis accounting entry"""
        
    def get_basic_ledger(self, start_date: Optional[str] = None, 
                         end_date: Optional[str] = None, 
                         account_type: Optional[str] = None) -> Dict[str, Any]:
        """Get simple general ledger"""
        
    def track_income_expense(self, transaction_type: str, amount: float, 
                           description: str, category: str = '', 
                           date: Optional[str] = None) -> Dict[str, Any]:
        """Track simple income and expense"""
        
    def get_income_expense_summary(self, period: str = 'month') -> Dict[str, Any]:
        """Get income and expense summary"""
        
    def get_financial_health_indicators(self) -> Dict[str, Any]:
        """Get basic financial health indicators"""
        
    def calculate_tax(self, amount: float, tax_type: str = 'vat', 
                     tax_rate: Optional[float] = None) -> Dict[str, Any]:
        """Calculate tax amounts"""
        
    def get_cash_position(self, date: Optional[str] = None) -> Dict[str, Any]:
        """Get current cash position"""
        
    def create_recurring_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create recurring transaction"""
        
    def get_recurring_transactions(self, status: Optional[str] = None) -> Dict[str, Any]:
        """Get recurring transactions"""
```

**Usage Examples:**

```python
# Create cash entry
cash_entry = fbs.accounting.create_cash_entry(
    entry_type='income',
    amount=1500.00,
    description='Product sales',
    category='revenue',
    date='2025-01-15'
)

# Get basic ledger
ledger = fbs.accounting.get_basic_ledger(
    start_date='2025-01-01',
    end_date='2025-01-31',
    account_type='revenue'
)

# Track income/expense
income = fbs.accounting.track_income_expense(
    transaction_type='income',
    amount=2500.00,
    description='Consulting services',
    category='professional_services'
)

# Get financial summary
summary = fbs.accounting.get_income_expense_summary(period='month')

# Calculate tax
tax_calc = fbs.accounting.calculate_tax(
    amount=1000.00,
    tax_type='vat',
    tax_rate=0.15
)

# Get cash position
cash_position = fbs.accounting.get_cash_position()

# Create recurring transaction
recurring = fbs.accounting.create_recurring_transaction({
    'type': 'expense',
    'amount': 500.00,
    'description': 'Monthly rent',
    'category': 'rent',
    'frequency': 'monthly',
    'start_date': '2025-01-01',
    'end_date': '2025-12-31'
})
```

### 7. **CacheInterface**

Manages solution-specific caching:

```python
class CacheInterface:
    """Interface for Cache Management operations"""
    
    def get_cache(self, key: str, database_name: Optional[str] = None) -> Dict[str, Any]:
        """Get cached value"""
        
    def set_cache(self, key: str, value: Any, expiry_hours: int = 24,
                  database_name: Optional[str] = None) -> Dict[str, Any]:
        """Set cache value"""
        
    def delete_cache(self, key: str, database_name: Optional[str] = None) -> Dict[str, Any]:
        """Delete cache entry"""
        
    def clear_cache(self, database_name: Optional[str] = None) -> Dict[str, Any]:
        """Clear all cache for database"""
        
    def get_cache_stats(self, database_name: Optional[str] = None) -> Dict[str, Any]:
        """Get cache statistics"""
```

**Usage Examples:**

```python
# Set cache
fbs.cache.set_cache(
    'customer_123',
    customer_data,
    expiry_hours=24
)

# Get cache
cached_customer = fbs.cache.get_cache('customer_123')

# Delete cache
fbs.cache.delete_cache('customer_123')

# Clear all cache
fbs.cache.clear_cache()

# Get cache statistics
cache_stats = fbs.cache.get_cache_stats()
```

## Advanced Development Patterns

### 1. **Custom Service Wrappers**

Create custom services that wrap FBS functionality:

```python
class CustomerService:
    """Custom customer management service"""
    
    def __init__(self, solution_name: str):
        self.fbs = FBSInterface(solution_name)
    
    def get_customer_summary(self, customer_id: int) -> Dict[str, Any]:
        """Get comprehensive customer information"""
        try:
            # Get Odoo customer data
            customer = self.fbs.odoo.get_record('res.partner', customer_id)
            
            if not customer['success']:
                return {'success': False, 'error': 'Customer not found'}
            
            # Get custom fields
            custom_fields = self.fbs.fields.get_custom_fields('res.partner', customer_id)
            
            # Get related documents
            documents = self.fbs.odoo.get_records(
                'ir.attachment',
                filters=[
                    ('res_model', '=', 'res.partner'),
                    ('res_id', '=', customer_id)
                ]
            )
            
            # Get financial data
            financial = self.fbs.accounting.get_basic_ledger(
                filters={'partner_id': customer_id}
            )
            
            return {
                'success': True,
                'data': {
                    'customer': customer['data'],
                    'custom_fields': custom_fields['data'],
                    'documents': documents['data'],
                    'financial': financial['data']
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def create_customer_with_profile(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create customer with complete profile"""
        try:
            # Create customer in Odoo
            customer = self.fbs.odoo.create_record('res.partner', {
                'name': customer_data['name'],
                'email': customer_data.get('email', ''),
                'phone': customer_data.get('phone', ''),
                'is_company': customer_data.get('is_company', False),
                'customer_rank': 1
            })
            
            if not customer['success']:
                return customer
            
            customer_id = customer['data']['id']
            
            # Add custom fields
            if customer_data.get('loyalty_tier'):
                self.fbs.fields.set_custom_field(
                    'res.partner',
                    customer_id,
                    'loyalty_tier',
                    customer_data['loyalty_tier']
                )
            
            if customer_data.get('customer_type'):
                self.fbs.fields.set_custom_field(
                    'res.partner',
                    customer_id,
                    'customer_type',
                    customer_data['customer_type']
                )
            
            # Create initial document if provided
            if customer_data.get('initial_document'):
                doc = self.fbs.odoo.create_record('ir.attachment', {
                    'name': customer_data['initial_document']['name'],
                    'res_model': 'res.partner',
                    'res_id': customer_id,
                    'datas': customer_data['initial_document']['content']
                })
            
            return {
                'success': True,
                'customer_id': customer_id,
                'message': 'Customer created successfully with profile'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

# Usage
customer_service = CustomerService('retail_solution')
customer_summary = customer_service.get_customer_summary(123)
new_customer = customer_service.create_customer_with_profile({
    'name': 'New Customer Ltd',
    'email': 'info@newcustomer.com',
    'loyalty_tier': 'silver',
    'customer_type': 'retail'
})
```

### 2. **Event-Driven Integration**

Use Django signals for automatic synchronization:

```python
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from your_app.models import Customer

@receiver(post_save, sender=Customer)
def sync_customer_with_odoo(sender, instance, created, **kwargs):
    """Sync customer changes with Odoo"""
    try:
        fbs = FBSInterface('your_solution')
        
        if created:
            # Create in Odoo
            odoo_customer = fbs.odoo.create_record('res.partner', {
                'name': instance.name,
                'email': instance.email,
                'phone': instance.phone,
                'is_company': instance.is_company
            })
            
            if odoo_customer['success']:
                # Store Odoo ID reference
                instance.odoo_id = odoo_customer['data']['id']
                instance.save(update_fields=['odoo_id'])
                
                # Add custom fields
                fbs.fields.set_custom_field(
                    'res.partner',
                    instance.odoo_id,
                    'customer_type',
                    instance.customer_type
                )
        else:
            # Update in Odoo
            if instance.odoo_id:
                fbs.odoo.update_record('res.partner', instance.odoo_id, {
                    'name': instance.name,
                    'email': instance.email,
                    'phone': instance.phone
                })
                
    except Exception as e:
        logger.error(f"Failed to sync customer with Odoo: {str(e)}")

@receiver(post_delete, sender=Customer)
def delete_customer_from_odoo(sender, instance, **kwargs):
    """Delete customer from Odoo when Django model is deleted"""
    try:
        if instance.odoo_id:
            fbs = FBSInterface('your_solution')
            fbs.odoo.delete_record('res.partner', instance.odoo_id)
    except Exception as e:
        logger.error(f"Failed to delete customer from Odoo: {str(e)}")
```

### 3. **Batch Operations**

Implement efficient batch processing:

```python
class BatchProcessor:
    """Efficient batch processing for FBS operations"""
    
    def __init__(self, solution_name: str):
        self.fbs = FBSInterface(solution_name)
        self.batch_size = 100
    
    def batch_create_partners(self, partner_data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create multiple partners efficiently"""
        results = []
        
        for i in range(0, len(partner_data_list), self.batch_size):
            batch = partner_data_list[i:i + self.batch_size]
            batch_results = self._process_partner_batch(batch)
            results.extend(batch_results)
        
        return results
    
    def _process_partner_batch(self, batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process a batch of partners"""
        results = []
        
        for partner_data in batch:
            try:
                # Create partner in Odoo
                result = self.fbs.odoo.create_record('res.partner', {
                    'name': partner_data['name'],
                    'email': partner_data.get('email', ''),
                    'is_company': partner_data.get('is_company', False)
                })
                
                if result['success']:
                    partner_id = result['data']['id']
                    
                    # Add custom fields in batch
                    custom_fields = partner_data.get('custom_fields', {})
                    for field_name, field_value in custom_fields.items():
                        self.fbs.fields.set_custom_field(
                            'res.partner',
                            partner_id,
                            field_name,
                            field_value
                        )
                    
                    results.append({
                        'success': True,
                        'partner_id': partner_id,
                        'original_data': partner_data
                    })
                else:
                    results.append({
                        'success': False,
                        'error': result.get('error'),
                        'original_data': partner_data
                    })
                    
            except Exception as e:
                results.append({
                    'success': False,
                    'error': str(e),
                    'original_data': partner_data
                })
        
        return results

# Usage
processor = BatchProcessor('retail_solution')
partner_data = [
    {'name': 'Company A', 'email': 'a@company.com', 'custom_fields': {'type': 'retail'}},
    {'name': 'Company B', 'email': 'b@company.com', 'custom_fields': {'type': 'wholesale'}},
    # ... more partners
]

results = processor.batch_create_partners(partner_data)
successful = [r for r in results if r['success']]
failed = [r for r in results if not r['success']]

print(f"Successfully created {len(successful)} partners")
print(f"Failed to create {len(failed)} partners")
```

### 4. **Error Handling and Fallbacks**

Implement robust error handling:

```python
class RobustFBSInterface:
    """FBS interface with robust error handling and fallbacks"""
    
    def __init__(self, solution_name: str):
        self.fbs = FBSInterface(solution_name)
        self.fallback_enabled = True
    
    def safe_odoo_operation(self, operation_func, *args, **kwargs):
        """Safely execute Odoo operations with error handling"""
        try:
            result = operation_func(*args, **kwargs)
            
            if not result.get('success'):
                logger.warning(f"Odoo operation failed: {result.get('error')}")
                
                if self.fallback_enabled:
                    return self._get_fallback_data(operation_func.__name__, *args, **kwargs)
                
                return result
            
            return result
            
        except Exception as e:
            logger.error(f"Odoo operation exception: {str(e)}")
            
            if self.fallback_enabled:
                return self._get_fallback_data(operation_func.__name__, *args, **kwargs)
            
            return {
                'success': False,
                'error': str(e),
                'fallback_used': True
            }
    
    def _get_fallback_data(self, operation_name: str, *args, **kwargs):
        """Get fallback data when Odoo is unavailable"""
        try:
            if operation_name == 'get_records':
                return self._fallback_get_records(*args, **kwargs)
            elif operation_name == 'create_record':
                return self._fallback_create_record(*args, **kwargs)
            # Add more fallback methods as needed
            
        except Exception as e:
            logger.error(f"Fallback operation failed: {str(e)}")
            return {
                'success': False,
                'error': f"Both Odoo and fallback failed: {str(e)}",
                'fallback_used': True
            }
    
    def _fallback_get_records(self, model_name: str, **kwargs):
        """Fallback for getting records from Django models"""
        try:
            # Map Odoo models to Django models
            model_mapping = {
                'res.partner': 'your_app.Customer',
                'ir.attachment': 'your_app.Document',
                # Add more mappings
            }
            
            if model_name in model_mapping:
                django_model = import_string(model_mapping[model_name])
                queryset = django_model.objects.all()
                
                # Apply filters if possible
                if kwargs.get('filters'):
                    queryset = self._apply_django_filters(queryset, kwargs['filters'])
                
                # Apply limit
                if kwargs.get('limit'):
                    queryset = queryset[:kwargs['limit']]
                
                return {
                    'success': True,
                    'data': list(queryset.values()),
                    'fallback_used': True
                }
            
            return {
                'success': False,
                'error': f'No fallback available for model: {model_name}',
                'fallback_used': True
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Fallback failed: {str(e)}',
                'fallback_used': True
            }

# Usage
robust_fbs = RobustFBSInterface('retail_solution')

# Safe Odoo operations
partners = robust_fbs.safe_odoo_operation(
    robust_fbs.fbs.odoo.get_records,
    'res.partner',
    limit=10
)

if partners.get('fallback_used'):
    print("Using fallback data - Odoo unavailable")
```

## Testing Strategies

### 1. **Unit Testing with Mocks**

```python
from django.test import TestCase
from unittest.mock import patch, MagicMock

class FBSInterfaceTest(TestCase):
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
    
    @patch('fbs_app.interfaces.FBSInterface')
    def test_virtual_fields(self, mock_fbs):
        # Mock virtual fields responses
        mock_fbs.fields.set_custom_field.return_value = {
            'success': True,
            'message': 'Field set successfully'
        }
        
        result = mock_fbs.fields.set_custom_field(
            'res.partner', 1, 'test_field', 'test_value'
        )
        self.assertTrue(result['success'])
```

### 2. **Integration Testing**

```python
class FBSIntegrationTestCase(TestCase):
    def setUp(self):
        self.solution_name = 'test_solution'
        self.fbs = FBSInterface(self.solution_name)
    
    def test_full_workflow(self):
        """Test complete business workflow"""
        # Create customer
        customer = self.fbs.odoo.create_record('res.partner', {
            'name': 'Test Customer',
            'is_company': True
        })
        
        self.assertTrue(customer['success'])
        customer_id = customer['data']['id']
        
        # Add custom field
        field_result = self.fbs.fields.set_custom_field(
            'res.partner',
            customer_id,
            'customer_type',
            'premium'
        )
        
        self.assertTrue(field_result['success'])
        
        # Get complete record
        complete_record = self.fbs.fields.merge_odoo_with_custom(
            'res.partner',
            customer_id,
            odoo_fields=['name', 'is_company']
        )
        
        self.assertTrue(complete_record['success'])
        self.assertIn('customer_type', complete_record['data'])
```

## Performance Optimization

### 1. **Caching Strategy**

```python
class CachedFBSInterface:
    """FBS interface with intelligent caching"""
    
    def __init__(self, solution_name: str):
        self.fbs = FBSInterface(solution_name)
        self.cache_ttl = 3600  # 1 hour
    
    def get_cached_partner(self, partner_id: int) -> Optional[Dict[str, Any]]:
        """Get partner with intelligent caching"""
        cache_key = f'partner_{partner_id}'
        
        # Try cache first
        cached = self.fbs.cache.get_cache(cache_key)
        if cached:
            return cached['data']
        
        # Get from Odoo
        partner = self.fbs.odoo.get_record('res.partner', partner_id)
        
        if partner['success']:
            # Cache for 1 hour
            self.fbs.cache.set_cache(
                cache_key,
                partner['data'],
                expiry_hours=self.cache_ttl // 3600
            )
            return partner['data']
        
        return None
    
    def invalidate_partner_cache(self, partner_id: int):
        """Invalidate partner cache when data changes"""
        cache_key = f'partner_{partner_id}'
        self.fbs.cache.delete_cache(cache_key)
```

### 2. **Batch Processing**

```python
def batch_process_with_cache(operation_func, items, cache_prefix: str):
    """Process items in batches with caching"""
    results = []
    
    for i in range(0, len(items), 100):  # Process in batches of 100
        batch = items[i:i + 100]
        batch_results = []
        
        for item in batch:
            # Check cache first
            cache_key = f'{cache_prefix}_{item["id"]}'
            cached = fbs.cache.get_cache(cache_key)
            
            if cached:
                batch_results.append(cached['data'])
            else:
                # Process item
                result = operation_func(item)
                if result['success']:
                    # Cache result
                    fbs.cache.set_cache(cache_key, result['data'], expiry_hours=24)
                    batch_results.append(result['data'])
                else:
                    batch_results.append({'error': result.get('error')})
        
        results.extend(batch_results)
    
    return results
```

## Best Practices

### 1. **Error Handling**
- Always check operation success status
- Implement comprehensive error logging
- Provide meaningful error messages
- Use fallback mechanisms when possible

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

### 4. **Maintainability**
- Follow consistent naming conventions
- Document complex operations
- Use type hints for clarity
- Implement comprehensive testing

## Next Steps

1. **Review [API Reference](API_REFERENCE.md)** - Complete interface documentation
2. **Check [Odoo Integration](ODOO_INTEGRATION.md)** - Master Odoo + Virtual Fields
3. **Study examples** - Review the provided code examples
4. **Start building** - Begin implementing FBS in your projects

---

**Ready to Build!** 🚀

You now have comprehensive knowledge of FBS service interfaces and development patterns. Start building powerful business applications with Odoo integration and FBS Virtual Fields technology.
