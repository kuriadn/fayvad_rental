# FBS Suite v2.0.4 - Developer Quick Reference

## 🎯 What is FBS?

**FBS (Fayvad Business Suite)** is an **embeddable Django business platform** that provides:
- **Odoo ERP Integration** - Full CRUD operations on Odoo models
- **Virtual Fields System** - Extend Odoo models without modification
- **Business Intelligence** - Dashboards, reports, and KPIs
- **Document Management** - File handling with metadata
- **License Management** - Feature control and access management
- **Workflow Engine** - State machine workflows and approvals

## 🚀 Quick Start (3 Steps)

### **1. Install**
```bash
pip install git+https://github.com/kuriadn/fbs.git@v2.0.4
```

### **2. Add to Django Settings**
```python
# settings.py
INSTALLED_APPS = [
    # ... Django apps ...
    'fbs_app',                    # Core business suite
    'fbs_dms',                    # Document management
    'fbs_license_manager',        # License management
]

# FBS Configuration
FBS_APP = {
    'ODOO_BASE_URL': 'http://localhost:8069',
    'DATABASE_USER': 'your_odoo_user',
    'DATABASE_PASSWORD': 'your_odoo_password',
}

# Database Routers
DATABASE_ROUTERS = ['fbs_app.routers.FBSDatabaseRouter']
```

### **3. Use in Views**
```python
from fbs_app.interfaces import FBSInterface

def dashboard(request):
    fbs = FBSInterface('your_solution_name')
    
    # Get business data
    dashboard_data = fbs.msme.get_dashboard()
    kpis = fbs.msme.calculate_kpis()
    
    # Get Odoo data
    partners = fbs.odoo.get_records('res.partner', limit=10)
    
    return render(request, 'dashboard.html', {
        'dashboard': dashboard_data,
        'kpis': kpis,
        'partners': partners
    })
```

## 🔧 Core Usage Patterns

### **Odoo Integration**
```python
fbs = FBSInterface('solution_name')

# Discover models
models = fbs.odoo.discover_models()

# CRUD operations
partners = fbs.odoo.get_records('res.partner', limit=10)
new_partner = fbs.odoo.create_record('res.partner', {
    'name': 'New Company',
    'email': 'info@company.com'
})
fbs.odoo.update_record('res.partner', partner_id, {'phone': '+1234567890'})
fbs.odoo.delete_record('res.partner', partner_id)
```

### **Virtual Fields**
```python
# Set custom data
fbs.fields.set_custom_field('res.partner', partner_id, 'tier', 'premium', 'char')

# Get custom data
tier = fbs.fields.get_custom_field('res.partner', partner_id, 'tier')

# Merge with Odoo data
full_record = fbs.fields.merge_odoo_with_custom(
    'res.partner', partner_id, ['name', 'email']
)
```

### **Business Management**
```python
# Setup business
business = fbs.msme.setup_business('services', {
    'company_name': 'My Company',
    'industry': 'technology',
    'employee_count': 25
})

# Get dashboard and KPIs
dashboard = fbs.msme.get_dashboard()
kpis = fbs.msme.calculate_kpis()
compliance = fbs.msme.get_compliance_status()
```

### **Document Management**
```python
# Upload document
doc = fbs.dms.upload_document(
    file_path='invoice.pdf',
    category='invoices',
    metadata={'partner_id': partner_id, 'amount': 1500.00}
)

# Search documents
invoices = fbs.dms.search_documents(
    category='invoices',
    filters={'partner_id': partner_id}
)
```

### **License Management**
```python
# Create license
license = fbs.license.create_license(
    plan_name='premium_plan',
    user_email='user@example.com',
    features=['advanced_analytics', 'api_access'],
    expiry_date='2025-12-31'
)

# Check validity
is_valid = fbs.license.validate_license(license_id)
```

## 🗄️ Database Architecture

### **Database Naming**
- **`fbs_system_db`** - Shared system components
- **`djo_{solution}_db`** - Django solution-specific data
- **`fbs_{solution}_db`** - Odoo solution-specific data

### **Database Routing**
```python
# FBSDatabaseRouter automatically routes:
# - License manager → default (system)
# - FBS app models → default (system)
# - DMS models → solution databases if specified, otherwise default
# - Your models → solution databases based on hints
```

### **Solution Isolation**
```python
# Each solution gets isolated databases
solution_name = "my_enterprise_solution"
# Creates: djo_my_enterprise_solution_db, fbs_my_enterprise_solution_db
# No cross-solution data leakage
```

## 🔐 Authentication & Security

### **Handshake Authentication**
```python
from fbs_app.services.auth_service import AuthService

auth_service = AuthService()
token = auth_service.create_handshake_token(user_id, expiry_hours=24)
is_valid = auth_service.validate_handshake_token(token)
```

### **Request Logging**
- All requests automatically logged
- Performance metrics captured
- User context and database operations tracked

## 📊 Business Intelligence

### **Dashboards & Reports**
```python
# Generate reports
reports = fbs.bi.generate_reports()

# Get charts
charts = fbs.bi.get_charts()

# Create custom dashboard
dashboard = fbs.bi.create_dashboard('sales_analytics', [
    'revenue_chart', 'customer_growth', 'top_products'
])
```

### **KPI Management**
```python
# Calculate KPIs
kpis = fbs.msme.calculate_kpis()

# Set thresholds
fbs.bi.set_kpi_threshold('revenue_growth', 15.0)

# Get alerts
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

# Process workflow step
result = fbs.workflows.process_workflow_step(
    workflow_id, 'approve', approver_id=manager_id
)
```

## 🧪 Testing

### **Test Configuration**
```python
# conftest.py
@pytest.fixture
def fbs_interface():
    from fbs_app.interfaces import FBSInterface
    return FBSInterface('test_solution')

# Mock FBS for testing
@patch('your_app.views.FBSInterface')
def test_dashboard(mock_fbs):
    mock_fbs_instance = MagicMock()
    mock_fbs_instance.msme.get_dashboard.return_value = {...}
    mock_fbs.return_value = mock_fbs_instance
```

## 🚨 Common Issues & Solutions

### **1. Django Settings Not Configured**
```python
# ❌ Error: Requested setting INSTALLED_APPS, but settings are not configured
# ✅ Solution: Configure Django before importing FBS

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')
django.setup()
```

### **2. Model Import Errors**
```python
# ❌ Error: cannot import name 'MSMEBusiness' from 'fbs_app.models'
# ✅ Solution: Use FBSInterface, not direct model imports

from fbs_app.interfaces import FBSInterface
fbs = FBSInterface('solution_name')
```

### **3. Database Connection Issues**
```python
# ❌ Error: connection to server at "localhost" failed
# ✅ Solution: Check environment variables

# Ensure these are set:
# FBS_DB_HOST, FBS_DB_PORT, FBS_DB_USER, FBS_DB_PASSWORD
# ODOO_BASE_URL, ODOO_USER, ODOO_PASSWORD
```

## 📚 Key Files & Locations

### **Core Files**
- **`fbs_app/interfaces.py`** - Main FBSInterface class
- **`fbs_app/services/`** - Business logic services
- **`fbs_app/routers.py`** - Database routing logic
- **`fbs_project/settings.py`** - Django configuration

### **Documentation**
- **`docs/CURSOR_DEVELOPER_GUIDE.md`** - Comprehensive developer guide
- **`docs/EMBEDDING_GUIDE.md`** - Step-by-step integration guide
- **`docs/API_REFERENCE.md`** - Complete API documentation
- **`docs/DEVELOPER_GUIDE.md`** - Architecture and patterns

### **Examples**
- **`solution_integration_example.py`** - Basic integration example
- **`test_solution_migrations.py`** - Migration testing
- **`install_v2.0.4.py`** - Installation script

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
# Use caching
fbs.cache.set('user_dashboard', dashboard_data, timeout=300)

# Batch operations
fbs.odoo.create_records_batch('res.partner', partners_list)

# Field filtering
fbs.odoo.get_records('res.partner', fields=['name', 'email'])
```

### **4. Security**
```python
# Validate permissions
if not user.has_perm('fbs_app.view_business_data'):
    raise PermissionDenied("Access denied")

# Sanitize input
cleaned_data = fbs.utils.sanitize_input(user_input)
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
- **This Guide**: Quick Reference
- **Cursor Developer Guide**: `docs/CURSOR_DEVELOPER_GUIDE.md`
- **Embedding Guide**: `docs/EMBEDDING_GUIDE.md`
- **API Reference**: `docs/API_REFERENCE.md`

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

*This quick reference provides essential information for developers and Cursor AI to quickly understand and use FBS. For detailed information, refer to the comprehensive guides in the docs/ directory.*
