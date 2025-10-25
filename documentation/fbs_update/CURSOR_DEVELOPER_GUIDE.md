# FBS Suite v2.0.4 - Cursor Developer Guide

## 🎯 Overview

This guide provides **developers and Cursor AI** with comprehensive information on embedding and using the **FBS (Fayvad Business Suite)** in Django projects. FBS is designed as an **embeddable business platform** that provides Odoo integration, document management, and license management capabilities.

## 🏗️ Architecture Summary

### **Core Design Principles**
- **Odoo as Primary Data Store**: All business data lives in Odoo ERP
- **Django as UI Layer**: Django models serve as UI references and business logic containers
- **Service-Oriented**: Business logic encapsulated in service classes
- **Multi-Tenant**: Solution-based isolation with dynamic database routing
- **Embeddable**: Designed to be integrated into larger Django solutions

### **Database Architecture**
```
┌─────────────────────────────────────────────────────────────┐
│                    Solution Architecture                     │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   Your App      │  │   FBS Apps      │  │   Django    │ │
│  │                 │  │                 │  │   Core      │ │
│  │ • Business      │  │ • fbs_app       │  │ • Auth      │ │
│  │ • UI/UX         │  │ • fbs_dms       │  │ • Admin     │ │
│  │ • Custom        │  │ • fbs_license   │  │ • Settings  │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Databases     │
                       │                 │
                       │ • fbs_system_db │
                       │ • djo_{sol}_db  │
                       │ • fbs_{sol}_db  │
                       └─────────────────┘
```

## 🚀 Quick Start - Embedding FBS

### **1. Install FBS Suite**

```bash
# From current directory (development)
pip install -e .

# From Git repository
pip install git+https://github.com/kuriadn/fbs.git@v2.0.4

# From PyPI (when available)
pip install fbs-suite==2.0.4
```

### **2. Add to Django Settings**

```python
# settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # FBS Apps
    'fbs_app',                    # Core business suite
    'fbs_dms',                    # Document management
    'fbs_license_manager',        # License management
]

# FBS Configuration
FBS_APP = {
    'ODOO_BASE_URL': 'http://your-odoo-server:8069',
    'ODOO_TIMEOUT': 30,
    'ODOO_MAX_RETRIES': 3,
    'DATABASE_USER': 'your_odoo_user',
    'DATABASE_PASSWORD': 'your_odoo_password',
}

# Database Routers
DATABASE_ROUTERS = [
    'fbs_app.routers.FBSDatabaseRouter',
]
```

### **3. Initialize FBS Interface**

```python
from fbs_app.interfaces import FBSInterface

# Initialize with your solution name
fbs = FBSInterface('your_solution_name')

# Check system health
health = fbs.get_system_health()
print(f"FBS Status: {health['status']}")
```

## 🔧 Core Usage Patterns

### **1. Odoo Integration**

```python
# Discover available models
models = fbs.odoo.discover_models()
print(f"Available models: {[m['name'] for m in models['data']]}")

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
fbs.odoo.update_record('res.partner', partner_id, {
    'phone': '+1234567890'
})

# Delete records
fbs.odoo.delete_record('res.partner', partner_id)
```

### **2. Virtual Fields System**

```python
# Set custom field data
fbs.fields.set_custom_field(
    'res.partner', 
    partner_id, 
    'customer_tier', 
    'premium', 
    'char'
)

# Get custom field data
tier = fbs.fields.get_custom_field('res.partner', partner_id, 'customer_tier')

# Merge Odoo data with custom fields
full_record = fbs.fields.merge_odoo_with_custom(
    'res.partner', 
    partner_id, 
    ['name', 'email', 'phone']
)
```

### **3. MSME Business Management**

```python
# Setup business
business_result = fbs.msme.setup_business('services', {
    'company_name': 'My Company',
    'industry': 'technology',
    'employee_count': 25
})

# Get dashboard
dashboard = fbs.msme.get_dashboard()

# Calculate KPIs
kpis = fbs.msme.calculate_kpis()

# Get compliance status
compliance = fbs.msme.get_compliance_status()
```

### **4. Document Management**

```python
# Upload documents
doc_result = fbs.dms.upload_document(
    file_path='invoice.pdf',
    category='invoices',
    metadata={
        'partner_id': partner_id,
        'amount': 1500.00,
        'due_date': '2024-12-31'
    }
)

# Search documents
invoices = fbs.dms.search_documents(
    category='invoices',
    filters={'partner_id': partner_id}
)

# Download document
fbs.dms.download_document(doc_id, 'downloads/')
```

### **5. License Management**

```python
# Create license
license_result = fbs.license.create_license(
    plan_name='premium_plan',
    user_email='user@example.com',
    features=['advanced_analytics', 'api_access'],
    expiry_date='2025-12-31'
)

# Check license validity
is_valid = fbs.license.validate_license(license_id)

# Get license details
license_info = fbs.license.get_license(license_id)
```

## 🗄️ Database Management

### **Database Naming Convention**

- **`fbs_system_db`**: Shared system components (licensing, DMS)
- **`djo_{solution}_db`**: Django solution-specific data
- **`fbs_{solution}_db`**: Odoo solution-specific data

### **Database Routing**

The `FBSDatabaseRouter` automatically routes models to appropriate databases:

```python
# License manager models → default (system database)
# FBS app models → default (system database)  
# DMS models → solution databases if specified, otherwise default
# Your app models → solution databases based on hints
```

### **Solution Isolation**

```python
# Each solution gets isolated databases
solution_name = "my_enterprise_solution"

# Django database: djo_my_enterprise_solution_db
# Odoo database: fbs_my_enterprise_solution_db

# No cross-solution data leakage
```

## 🔐 Authentication & Security

### **Handshake Authentication**

```python
# FBS uses token-based authentication
from fbs_app.services.auth_service import AuthService

auth_service = AuthService()
token = auth_service.create_handshake_token(user_id, expiry_hours=24)

# Validate token
is_valid = auth_service.validate_handshake_token(token)
```

### **Request Logging**

```python
# All requests are logged with performance metrics
# Middleware automatically captures:
# - Request details
# - Response time
# - User context
# - Database operations
```

## 📊 Business Intelligence

### **Dashboard & Reports**

```python
# Generate business reports
reports = fbs.bi.generate_reports()

# Get interactive charts
charts = fbs.bi.get_charts()

# Create custom dashboards
dashboard = fbs.bi.create_dashboard('sales_analytics', [
    'revenue_chart',
    'customer_growth',
    'top_products'
])
```

### **KPI Management**

```python
# Calculate business KPIs
kpis = fbs.msme.calculate_kpis()

# Set KPI thresholds
fbs.bi.set_kpi_threshold('revenue_growth', 15.0)

# Get KPI alerts
alerts = fbs.bi.get_kpi_alerts()
```

## 🔄 Workflow Management

### **State Machine Workflows**

```python
# Create approval workflow
workflow = fbs.workflows.create_approval_request(
    'purchase_approval',
    requester_id=user_id,
    amount=5000.00,
    description='Office equipment purchase'
)

# Get active workflows
active_workflows = fbs.workflows.get_active_workflows()

# Process workflow step
result = fbs.workflows.process_workflow_step(
    workflow_id, 
    'approve', 
    approver_id=manager_id
)
```

## 🧪 Testing & Development

### **Test Configuration**

```python
# conftest.py
import pytest
from django.conf import settings

@pytest.fixture(scope='session')
def django_db_setup():
    settings.DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }

@pytest.fixture
def fbs_interface():
    from fbs_app.interfaces import FBSInterface
    return FBSInterface('test_solution')
```

### **Service Testing**

```python
# test_services.py
def test_odoo_integration(fbs_interface):
    """Test Odoo integration"""
    models = fbs_interface.odoo.discover_models()
    assert 'res.partner' in [m['name'] for m in models['data']]

def test_virtual_fields(fbs_interface):
    """Test virtual fields system"""
    # Test field operations
    fbs_interface.fields.set_custom_field(
        'res.partner', 1, 'test_field', 'test_value', 'char'
    )
    
    value = fbs_interface.fields.get_custom_field(
        'res.partner', 1, 'test_field'
    )
    assert value == 'test_value'
```

## 🚨 Common Issues & Solutions

### **1. Django Settings Not Configured**

```python
# ❌ Error: Requested setting INSTALLED_APPS, but settings are not configured
# ✅ Solution: Configure Django before importing FBS services

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')
django.setup()

# Now import FBS services
from fbs_app.interfaces import FBSInterface
```

### **2. Database Connection Issues**

```python
# ❌ Error: connection to server at "localhost" failed
# ✅ Solution: Check environment variables and database settings

# Ensure these are set:
# FBS_DB_HOST, FBS_DB_PORT, FBS_DB_USER, FBS_DB_PASSWORD
# ODOO_BASE_URL, ODOO_USER, ODOO_PASSWORD
```

### **3. Model Import Errors**

```python
# ❌ Error: cannot import name 'MSMEBusiness' from 'fbs_app.models'
# ✅ Solution: Use lazy imports in services

# Services use lazy imports to avoid Django configuration issues
# Import services, not models directly
from fbs_app.interfaces import FBSInterface
fbs = FBSInterface('solution_name')
```

### **4. Migration Issues**

```python
# ❌ Error: relation "table_name" already exists
# ✅ Solution: Fake initial migrations for existing tables

python manage.py migrate --fake fbs_app 0001
python manage.py migrate --fake fbs_dms 0001
python manage.py migrate --fake fbs_license_manager 0001
```

## 📚 API Reference

### **FBSInterface Methods**

```python
class FBSInterface:
    def __init__(self, solution_name: str)
    def get_system_health() -> Dict[str, Any]
    
    # Sub-interfaces
    odoo: OdooIntegrationInterface
    fields: VirtualFieldsInterface  
    msme: MSMEInterface
    dms: DMSInterface
    license: LicenseInterface
    bi: BusinessIntelligenceInterface
    workflows: WorkflowInterface
    accounting: AccountingInterface
    compliance: ComplianceInterface
    notifications: NotificationInterface
```

### **Service Classes**

```python
# Core Services
MSMEService              # MSME business management
BusinessIntelligenceService  # BI and reporting
WorkflowService          # Workflow management
ComplianceService        # Compliance tracking
NotificationService      # Alerts and notifications

# Integration Services  
OdooClient              # Odoo XML-RPC client
FieldMergerService      # Virtual fields management
DatabaseService         # Database operations
CacheService            # Caching system
```

## 🎯 Best Practices

### **1. Solution Naming**
- Use descriptive, lowercase names: `rental_system`, `inventory_tracker`
- Avoid special characters and spaces
- Keep names under 20 characters

### **2. Error Handling**
```python
try:
    result = fbs.odoo.create_record('res.partner', partner_data)
    if result['success']:
        print("✅ Partner created successfully")
    else:
        print(f"⚠️  Creation failed: {result.get('message')}")
        
except Exception as e:
    print(f"❌ Operation failed: {str(e)}")
```

### **3. Performance Optimization**
```python
# Use caching for frequently accessed data
fbs.cache.set('user_dashboard', dashboard_data, timeout=300)

# Batch operations for multiple records
fbs.odoo.create_records_batch('res.partner', partners_list)

# Use field filtering to reduce data transfer
fbs.odoo.get_records('res.partner', fields=['name', 'email'])
```

### **4. Security Considerations**
```python
# Always validate user permissions
if not user.has_perm('fbs_app.view_business_data'):
    raise PermissionDenied("Access denied")

# Sanitize input data
cleaned_data = fbs.utils.sanitize_input(user_input)

# Use parameterized queries (handled automatically by Odoo client)
```

## 🔄 Version Migration

### **From v2.0.3 to v2.0.4**

```python
# Key changes:
# 1. Model naming convention updated (DMS_, LIC_ prefixes)
# 2. Database architecture simplified
# 3. Service interfaces consolidated
# 4. Lazy imports implemented for better embedding

# Migration steps:
# 1. Update model references in your code
# 2. Regenerate migrations if needed
# 3. Test all integrations
# 4. Update version references
```

## 📞 Support & Resources

### **Documentation**
- **This Guide**: Cursor Developer Guide
- **Integration Guide**: `docs/INTEGRATION.md`
- **API Reference**: `docs/API_REFERENCE.md`
- **Developer Guide**: `docs/DEVELOPER_GUIDE.md`

### **Examples**
- **Solution Integration**: `solution_integration_example.py`
- **Test Scripts**: `test_*.py` files
- **Installation**: `install_v2.0.4.py`

### **Contact**
- **Email**: team@fayvad.com
- **Issues**: GitHub repository issues
- **Documentation**: Check inline code comments

---

**FBS Suite v2.0.4** - Ready for production embedding! 🚀

*This guide follows DRY and KISS principles, providing comprehensive coverage without over-engineering or hallucinations.*
