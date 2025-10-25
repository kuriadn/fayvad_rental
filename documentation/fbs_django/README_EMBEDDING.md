# FBS Suite v4.0.0 - Quick Embedding Guide

FBS Suite is a **headless, embeddable business framework** for Django applications.

## 🚀 Quick Start (5 minutes)

### 1. Install
```bash
pip install fbs-django==4.0.0
```

### 2. Configure
```python
# settings.py
INSTALLED_APPS = [
    'fbs_django.apps.core',
    'fbs_django.apps.dms',  # Add services you need
    # ... other FBS apps
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_system_db',
        'USER': 'admin',
        'PASSWORD': 'admin',
        # ... connection details
    }
}

DATABASE_ROUTERS = ['fbs_django.apps.core.database_router.FBSDatabaseRouter']
```

### 3. Embed in Your Code
```python
# views.py
from fbs_django.apps.core.services import FBSInterface

def my_view(request):
    # Direct FBS instantiation (NO HTTP!)
    fbs = FBSInterface("my_solution")

    # Direct service calls
    documents = fbs.dms.list_documents()
    analytics = fbs.bi.get_dashboard()

    return render(request, 'template.html', {
        'documents': documents,
        'analytics': analytics,
    })
```

## 📊 What You Get

### 16 Business Services
- **FBSInterface** - Main orchestrator
- **DocumentService** - File & document management
- **LicenseService** - Feature access control
- **MSMEService** - Small business management
- **BIService** - Business intelligence & analytics
- **WorkflowService** - Process automation
- **AccountingService** - Financial operations
- **ComplianceService** - Regulatory compliance
- **OdooService** - ERP integration
- **And 7 more specialized services**

### Zero HTTP Overhead
```python
# Traditional approach (HTTP calls)
response = requests.post('http://api.example.com/documents')
documents = response.json()

# FBS approach (direct calls)
fbs = FBSInterface("solution")
documents = fbs.dms.list_documents()  # Instant!
```

### Multi-Tenant Architecture
```python
# Automatic tenant isolation
solution_a = FBSInterface("company_a")  # Uses djo_company_a_db
solution_b = FBSInterface("company_b")  # Uses djo_company_b_db

# Data automatically isolated
data_a = solution_a.dms.list_documents()
data_b = solution_b.dms.list_documents()
```

## 🛠️ Integration Patterns

### Basic Embedding
```python
# In any Django view, model, or service
from fbs_django.apps.core.services import FBSInterface

fbs = FBSInterface("your_solution_name")

# Access any service directly
dms = fbs.dms
workflows = fbs.workflows
analytics = fbs.bi
```

### Business Logic Integration
```python
class MyBusinessService:
    def __init__(self):
        self.fbs = FBSInterface("my_company")

    def process_order(self, order_data):
        # Chain FBS services
        document = self.fbs.dms.create_document(order_data)
        workflow = self.fbs.workflows.start_workflow("order_processing", document)
        notification = self.fbs.notifications.send_alert(workflow)

        return {
            'document': document,
            'workflow': workflow,
            'notification': notification
        }
```

### API Integration
```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'fbs_django.apps.core.authentication.FBSTokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'fbs_django.apps.core.permissions.FBSLicensePermission',
    ],
}

# urls.py
urlpatterns = [
    path('api/fbs/', include('fbs_django.apps.core.urls')),
]
```

## 🔧 Configuration

### Database Setup
```python
# System database (fbs_system_db)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'fbs_system_db',
        'USER': 'fayvad',      # System user
        'PASSWORD': 'MeMiMo@0207',
    }
}

# FBS creates solution databases automatically:
# - djo_{solution}_db (Django solution data)
# - fbs_{solution}_db (Odoo ERP data)
```

### Odoo Integration (Optional)
```python
ODOO_CONFIG = {
    'BASE_URL': 'http://localhost:8069',
    'USERNAME': 'fayvad',
    'PASSWORD': 'MeMiMo@0207',
}
```

## 📚 Documentation

- **[FBS_EMBEDDING_GUIDE.md](FBS_EMBEDDING_GUIDE.md)** - Comprehensive integration guide
- **[fbs_integration_examples.py](fbs_integration_examples.py)** - Code examples
- **[DJANGO_FBS_IMPLEMENTATION_GUIDE.md](DJANGO_FBS_IMPLEMENTATION_GUIDE.md)** - Technical details

## 🎯 Key Benefits

✅ **Performance** - Direct method calls, no HTTP overhead
✅ **Simplicity** - Drop-in business services
✅ **Scalability** - Multi-tenant architecture
✅ **Security** - License-based access control
✅ **Integration** - Odoo ERP connectivity
✅ **Maintainability** - Clean separation of concerns

## 🚀 Next Steps

1. **Install FBS**: `pip install fbs-django==4.0.0`
2. **Configure database** in your `settings.py`
3. **Import FBSInterface** in your code
4. **Call services directly** - no API setup needed!
5. **Deploy** with confidence

**Ready to embed enterprise-grade business logic in minutes!** 🎉
