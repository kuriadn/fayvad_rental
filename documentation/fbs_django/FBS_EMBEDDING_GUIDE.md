# FBS Suite v4.0.0 - Embedding Guide

## Overview

FBS Suite v4.0.0 is a **headless, embeddable business logic framework** built on Django. It provides enterprise-grade business services that can be directly embedded into any Python application without HTTP overhead.

### Key Features
- **Zero HTTP calls** - Direct service instantiation and method calls
- **16 business services** - MSME, BI, workflows, accounting, compliance, etc.
- **Multi-tenant architecture** - Database-level solution isolation
- **License-based feature control** - Granular access management
- **Odoo ERP integration** - Seamless ERP connectivity
- **Django ORM integration** - Full Django compatibility

### Architecture
```
Host Django Application
├── Your views, templates, URLs
├── Your business logic
└── FBS Services (embedded)
    ├── FBSInterface (orchestrator)
    ├── DocumentService (DMS)
    ├── LicenseService (licensing)
    ├── OdooService (ERP)
    └── [14 other services]
```

## Prerequisites

### System Requirements
- Python 3.10+
- Django 4.2+
- PostgreSQL 12+
- Redis 6+ (optional, for caching)
- Odoo 16+ (optional, for ERP integration)

### Host Application Setup
Your Django application must have:
- Django project structure
- Database configuration
- URL configuration
- Settings module

## Installation

### 1. Install FBS Package
```bash
pip install fbs-django==4.0.0
```

### 2. Add to INSTALLED_APPS
```python
# settings.py
INSTALLED_APPS = [
    # Your existing apps
    'django.contrib.auth',
    'rest_framework',

    # FBS apps
    'fbs_django.apps.core',
    'fbs_django.apps.dms',
    'fbs_django.apps.licensing',
    'fbs_django.apps.odoo_integration',
    # Add other FBS apps as needed
]
```

### 3. Configure URLs
```python
# urls.py
from django.urls import path, include

urlpatterns = [
    # Your existing URLs

    # FBS API endpoints (optional)
    path('api/', include([
        path('fbs/', include('fbs_django.apps.core.urls')),
        path('dms/', include('fbs_django.apps.dms.urls')),
        # Add other FBS URLs as needed
    ])),
]
```

## Database Configuration

### Multi-Database Setup
FBS uses multi-tenant database routing:

```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_system_db',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# FBS dynamic routing
DATABASE_ROUTERS = ['fbs_django.apps.core.database_router.FBSDatabaseRouter']
```

### Database Naming Convention
FBS creates solution-specific databases:
- System DB: `fbs_system_db` (shared system data)
- Solution DBs: `djo_{solution_name}_db` (tenant data)
- Odoo DBs: `fbs_{solution_name}_db` (ERP data)

## FBS Configuration

### Basic Settings
```python
# settings.py
FBS_CONFIG = {
    'MODULE_TEMPLATES_DIR': '/path/to/fbs/templates',
    'UPLOAD_DIR': '/path/to/uploads',
    'LICENSE_ENCRYPTION_KEY': 'your-license-key',
    'REDIS_URL': 'redis://localhost:6379/0',
    'CACHE_TIMEOUT': 300,
    'MAX_UPLOAD_SIZE': 10485760,  # 10MB
}
```

### Odoo Integration (Optional)
```python
# settings.py
ODOO_CONFIG = {
    'BASE_URL': 'http://localhost:8069',
    'DB': 'odoo',
    'USERNAME': 'fayvad',
    'PASSWORD': 'MeMiMo@0207',
    'TIMEOUT': 30,
    'MAX_RETRIES': 3,
}
```

## Service Integration

### Basic FBS Embedding Pattern
```python
# views.py or services.py in your app
from fbs_django.apps.core.services import FBSInterface

def my_business_view(request):
    # Direct FBS instantiation (no HTTP!)
    fbs = FBSInterface(solution_name="my_solution")

    # Direct service access (lazy loading)
    dms = fbs.dms
    license_svc = fbs.license

    # Direct method calls (business logic)
    documents = dms.list_documents(user_id=request.user.id)
    license_info = license_svc.get_license_info()

    return render(request, 'my_template.html', {
        'documents': documents,
        'license': license_info,
    })
```

### Service-Specific Integration
```python
# For document management
from fbs_django.apps.dms.services import DocumentService

def upload_document(request):
    fbs = FBSInterface("my_solution")
    dms = fbs.dms

    # Direct DMS operations
    result = dms.create_document(
        document_data=request.POST,
        created_by=str(request.user.id),
        file_obj=request.FILES.get('file')
    )

    return JsonResponse(result)
```

### Odoo Integration
```python
# For ERP operations
from fbs_django.apps.odoo_integration.services import OdooService

def sync_customer_data(request):
    fbs = FBSInterface("my_solution")
    odoo = fbs.odoo

    # Direct Odoo operations
    customers = odoo.search_read_records(
        model_name='res.partner',
        domain=[('customer', '=', True)],
        fields=['name', 'email', 'phone']
    )

    return JsonResponse({'customers': customers})
```

## Authentication & Authorization

### FBS Token Authentication
```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'fbs_django.apps.core.authentication.FBSTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'fbs_django.apps.core.permissions.FBSLicensePermission',
    ],
}
```

### License-Based Access Control
```python
# In your views/services
def enterprise_feature(request):
    fbs = FBSInterface("my_solution")

    # FBS checks license automatically
    try:
        bi_service = fbs.bi  # License checked here
        analytics = bi_service.get_dashboard()
        return JsonResponse(analytics)
    except ValueError as e:
        # Feature not licensed
        return JsonResponse({'error': str(e)}, status=403)
```

## Database Operations

### Solution Context Management
```python
# Set current solution context
from fbs_django.apps.core.middleware.database_router import set_current_solution

def tenant_operation(request, tenant_id):
    # Set solution context for database routing
    set_current_solution(tenant_id)

    fbs = FBSInterface(tenant_id)

    # Operations now route to correct database
    documents = fbs.dms.list_documents()

    return JsonResponse({'documents': documents})
```

### Multi-Tenant Queries
```python
# FBS handles tenant isolation automatically
def cross_tenant_view(request):
    # Each FBS instance operates within its solution
    solution_a = FBSInterface("solution_a")
    solution_b = FBSInterface("solution_b")

    data_a = solution_a.dms.get_statistics()
    data_b = solution_b.dms.get_statistics()

    # Data automatically isolated by solution
    return JsonResponse({
        'solution_a': data_a,
        'solution_b': data_b,
    })
```

## Workflow Integration

### Integrated Workflows
```python
# Use FBS integrated workflows
def discover_and_extend(request):
    fbs = FBSInterface("my_solution")

    # Single method call triggers full workflow
    result = fbs.discover_and_extend(
        user_id=str(request.user.id),
        tenant_id="my_solution"
    )

    return JsonResponse(result)
```

### Custom Workflow Integration
```python
def custom_business_process(request):
    fbs = FBSInterface("my_solution")

    # Chain FBS services for custom workflows
    document = fbs.dms.create_document(request.POST)
    workflow = fbs.workflows.start_workflow("approval", document)
    notification = fbs.notifications.send_alert(workflow)

    return JsonResponse({
        'document': document,
        'workflow': workflow,
        'notification': notification,
    })
```

## Error Handling & Monitoring

### FBS Health Checks
```python
def system_health(request):
    fbs = FBSInterface("my_solution")

    # FBS provides comprehensive health status
    health = fbs.get_system_health()

    return JsonResponse(health)
```

### Exception Handling
```python
def safe_fbs_operation(request):
    try:
        fbs = FBSInterface("my_solution")
        result = fbs.some_operation(request.data)
        return JsonResponse(result)
    except ValueError as e:
        # FBS license/feature errors
        return JsonResponse({'error': str(e)}, status=403)
    except ConnectionError as e:
        # Odoo/database connection issues
        return JsonResponse({'error': 'Service unavailable'}, status=503)
    except Exception as e:
        # General FBS errors
        logger.error(f"FBS operation failed: {e}")
        return JsonResponse({'error': 'Operation failed'}, status=500)
```

## Best Practices

### 1. Service Instantiation
```python
# ✅ Good: Reuse FBS instances
fbs = FBSInterface("my_solution")

# Use throughout request lifecycle
documents = fbs.dms.list_documents()
license = fbs.license.get_info()

# ❌ Avoid: Multiple instantiations
dms = FBSInterface("my_solution").dms
license = FBSInterface("my_solution").license
```

### 2. Solution Context
```python
# ✅ Good: Set solution context early
set_current_solution(solution_name)
fbs = FBSInterface(solution_name)

# ❌ Avoid: Context switching mid-operation
fbs = FBSInterface("solution_a")
set_current_solution("solution_b")  # Confusing!
```

### 3. Error Handling
```python
# ✅ Good: Handle FBS-specific errors
try:
    result = fbs.operation()
except ValueError:
    # License/feature restrictions
except ConnectionError:
    # External service issues
```

### 4. Resource Management
```python
# ✅ Good: FBS handles connection pooling
# No manual connection management needed

# ✅ Good: Use caching when appropriate
cache = fbs.cache
cached_data = cache.get('key')
```

## Migration from Direct Implementation

### Before (Direct Implementation)
```python
# Your custom business logic
def create_business_entity(data):
    # Custom validation
    # Custom database operations
    # Custom integrations
    pass
```

### After (FBS Embedded)
```python
# FBS handles business logic
def create_business_entity(request):
    fbs = FBSInterface("my_solution")

    # FBS provides validated, integrated operations
    result = fbs.business_service.create_entity(request.POST)

    # Your presentation logic only
    return JsonResponse(result)
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Errors
```python
# Check database configuration
python manage.py dbshell  # Test default DB
python manage.py shell -c "from fbs_django.apps.core.services import FBSInterface; fbs = FBSInterface('test')"
```

#### 2. License Errors
```python
# Check license configuration
fbs = FBSInterface("my_solution")
license_info = fbs.get_license_info()
print(license_info)  # Debug license status
```

#### 3. Odoo Connection Issues
```python
# Test Odoo connectivity
fbs = FBSInterface("my_solution")
health = fbs.get_system_health()
print(health['components']['odoo'])  # Check Odoo status
```

#### 4. Import Errors
```python
# Ensure FBS is properly installed
pip list | grep fbs-django

# Check INSTALLED_APPS
python manage.py check
```

## Performance Optimization

### 1. Service Caching
```python
# FBS includes built-in caching
fbs = FBSInterface("my_solution")
cache = fbs.cache

# Cache expensive operations
data = cache.get('expensive_operation')
if not data:
    data = fbs.expensive_operation()
    cache.set('expensive_operation', data, 3600)
```

### 2. Lazy Loading
```python
# FBS services load on-demand
fbs = FBSInterface("my_solution")

# Only loads when accessed
dms = fbs.dms  # Loads here
bi = fbs.bi    # Loads here when needed
```

### 3. Connection Pooling
```python
# FBS manages database connections automatically
# No manual connection handling needed
# Django ORM handles pooling
```

## Security Considerations

### 1. Database Isolation
- FBS ensures tenant data isolation
- Solution contexts prevent data leakage
- License checks enforce feature access

### 2. Authentication
- Use FBSTokenAuthentication for APIs
- Implement proper user session management
- Validate solution access permissions

### 3. Input Validation
```python
# FBS includes input validation
# But validate at your application layer too
def safe_operation(request):
    # Your validation
    if not request.user.has_perm('app.operation'):
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    # FBS operation (already validated)
    fbs = FBSInterface("my_solution")
    result = fbs.operation(request.POST)

    return JsonResponse(result)
```

## Summary

FBS Suite v4.0.0 provides a complete embeddable business framework that integrates seamlessly into any Django application. The key benefits:

- **Zero HTTP overhead** - Direct service calls
- **Complete business logic** - 16 enterprise services
- **Multi-tenant ready** - Automatic data isolation
- **License managed** - Granular feature control
- **Odoo integrated** - ERP connectivity
- **Django native** - Full framework compatibility

**Integration Pattern:**
1. Install FBS package
2. Configure databases and settings
3. Import FBSInterface in your views/services
4. Call FBS methods directly
5. Handle responses in your templates/views

This approach maintains clean separation between your presentation logic and FBS business logic while providing enterprise-grade functionality with minimal integration effort.
