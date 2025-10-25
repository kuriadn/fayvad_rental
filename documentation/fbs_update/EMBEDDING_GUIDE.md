# FBS Suite v2.0.4 - Embedding Guide

## 🎯 Overview

This guide provides **step-by-step instructions** for embedding the **FBS (Fayvad Business Suite)** into your Django projects. FBS is designed as an **embeddable business platform** that transforms your Django applications into Odoo-powered business solutions.

## 🏗️ Architecture Understanding

### **What FBS Provides**
- **Odoo Integration**: Full CRUD operations on Odoo models
- **Virtual Fields**: Extend Odoo models without modification
- **Business Intelligence**: Dashboards, reports, and KPIs
- **Document Management**: File handling with metadata
- **License Management**: Feature control and access management
- **Workflow Engine**: State machine workflows and approvals

### **What You Provide**
- **Django Project**: Your main application
- **Solution Logic**: Business-specific functionality
- **UI/UX**: User interface and experience
- **Custom Models**: Solution-specific data models

### **Integration Pattern**
```
┌─────────────────────────────────────────────────────────────┐
│                    Your Django Solution                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   Your App      │  │   FBS Apps      │  │   Django    │ │
│  │                 │  │                 │  │   Core      │ │
│  │ • Views         │  │ • fbs_app       │  │ • Auth      │ │
│  │ • Templates     │  │ • fbs_dms       │  │ • Admin     │ │
│  │ • URLs          │  │ • fbs_license   │  │ • Settings  │ │
│  │ • Custom Logic  │  │                 │  │             │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   FBSInterface  │
                       │ (Service Layer) │
                       └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Odoo ERP      │
                       │ (Data Store)    │
                       └─────────────────┘
```

## 🚀 Step-by-Step Integration

### **Step 1: Install FBS Suite**

```bash
# Option 1: Install from current directory (development)
cd /path/to/fbs
pip install -e .

# Option 2: Install from Git repository
pip install git+https://github.com/kuriadn/fbs.git@v2.0.4

# Option 3: Install from PyPI (when available)
pip install fbs-suite==2.0.4
```

### **Step 2: Add FBS to Your Django Settings**

```python
# your_project/settings.py

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Your apps
    'your_app',
    
    # FBS Apps
    'fbs_app',                    # Core business suite
    'fbs_dms',                    # Document management
    'fbs_license_manager',        # License management
]

# FBS Configuration
FBS_APP = {
    # Database configuration
    'DATABASE_ENGINE': 'django.db.backends.postgresql',
    'DATABASE_HOST': os.environ.get('FBS_DB_HOST', 'localhost'),
    'DATABASE_PORT': os.environ.get('FBS_DB_PORT', '5432'),
    'DATABASE_USER': os.environ.get('FBS_DB_USER', 'odoo'),
    'DATABASE_PASSWORD': os.environ.get('FBS_DB_PASSWORD', 'your_password'),
    
    # Odoo integration
    'ODOO_BASE_URL': os.environ.get('ODOO_BASE_URL', 'http://localhost:8069'),
    'ODOO_TIMEOUT': 30,
    'ODOO_MAX_RETRIES': 3,
    
    # Features
    'ENABLE_MSME_FEATURES': True,
    'ENABLE_BI_FEATURES': True,
    'ENABLE_WORKFLOW_FEATURES': True,
    'ENABLE_COMPLIANCE_FEATURES': True,
    'ENABLE_ACCOUNTING_FEATURES': True,
}

# Database Routers
DATABASE_ROUTERS = [
    'fbs_app.routers.FBSDatabaseRouter',
]

# Database Configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'fbs_system_db',
        'USER': os.environ.get('FBS_DB_USER', 'odoo'),
        'PASSWORD': os.environ.get('FBS_DB_PASSWORD', 'your_password'),
        'HOST': os.environ.get('FBS_DB_HOST', 'localhost'),
        'PORT': os.environ.get('FBS_DB_PORT', '5432'),
    },
    # Solution-specific databases will be added dynamically
}
```

### **Step 3: Create Solution-Specific Settings**

```python
# your_project/solution_settings.py

def get_solution_databases(solution_name):
    """Generate database configuration for a specific solution"""
    return {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'fbs_system_db',
            'USER': os.environ.get('FBS_DB_USER', 'odoo'),
            'PASSWORD': os.environ.get('FBS_DB_PASSWORD', 'your_password'),
            'HOST': os.environ.get('FBS_DB_HOST', 'localhost'),
            'PORT': os.environ.get('FBS_DB_PORT', '5432'),
        },
        f'djo_{solution_name}_db': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': f'djo_{solution_name}_db',
            'USER': os.environ.get('FBS_DB_USER', 'odoo'),
            'PASSWORD': os.environ.get('FBS_DB_PASSWORD', 'your_password'),
            'HOST': os.environ.get('FBS_DB_HOST', 'localhost'),
            'PORT': os.environ.get('FBS_DB_PORT', '5432'),
        },
        f'fbs_{solution_name}_db': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': f'fbs_{solution_name}_db',
            'USER': os.environ.get('FBS_DB_USER', 'odoo'),
            'PASSWORD': os.environ.get('FBS_DB_PASSWORD', 'your_password'),
            'HOST': os.environ.get('FBS_DB_HOST', 'localhost'),
            'PORT': os.environ.get('FBS_DB_PORT', '5432'),
        }
    }
```

### **Step 4: Initialize FBS in Your Views**

```python
# your_app/views.py

from django.shortcuts import render
from django.http import JsonResponse
from fbs_app.interfaces import FBSInterface

def business_dashboard(request):
    """Business dashboard view using FBS"""
    
    # Get solution name from request or session
    solution_name = request.session.get('solution_name', 'default_solution')
    
    # Initialize FBS interface
    fbs = FBSInterface(solution_name)
    
    try:
        # Get business data from FBS
        dashboard_data = fbs.msme.get_dashboard()
        kpis = fbs.msme.calculate_kpis()
        
        # Get Odoo data
        partners = fbs.odoo.get_records('res.partner', limit=10)
        
        context = {
            'dashboard': dashboard_data,
            'kpis': kpis,
            'partners': partners,
            'solution_name': solution_name,
        }
        
        return render(request, 'your_app/dashboard.html', context)
        
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'status': 'error'
        }, status=500)

def create_partner(request):
    """Create partner using FBS Odoo integration"""
    
    if request.method == 'POST':
        solution_name = request.session.get('solution_name', 'default_solution')
        fbs = FBSInterface(solution_name)
        
        try:
            partner_data = {
                'name': request.POST.get('name'),
                'email': request.POST.get('email'),
                'phone': request.POST.get('phone'),
                'is_company': True,
            }
            
            result = fbs.odoo.create_record('res.partner', partner_data)
            
            if result['success']:
                return JsonResponse({
                    'success': True,
                    'partner_id': result['data']['id'],
                    'message': 'Partner created successfully'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': result.get('message', 'Unknown error')
                }, status=400)
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return render(request, 'your_app/create_partner.html')
```

### **Step 5: Create Solution Management Views**

```python
# your_app/views.py

def solution_setup(request):
    """Setup solution with FBS"""
    
    if request.method == 'POST':
        solution_name = request.POST.get('solution_name')
        
        if not solution_name:
            return JsonResponse({'error': 'Solution name required'}, status=400)
        
        try:
            # Initialize FBS for this solution
            fbs = FBSInterface(solution_name)
            
            # Setup business
            business_result = fbs.msme.setup_business(
                business_type='services',
                config={
                    'company_name': request.POST.get('company_name'),
                    'industry': request.POST.get('industry'),
                    'employee_count': int(request.POST.get('employee_count', 0)),
                }
            )
            
            if business_result['success']:
                # Store solution name in session
                request.session['solution_name'] = solution_name
                
                return JsonResponse({
                    'success': True,
                    'message': f'Solution {solution_name} setup successfully',
                    'business_id': business_result['data']['business_id']
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': business_result.get('message', 'Business setup failed')
                }, status=400)
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return render(request, 'your_app/solution_setup.html')

def switch_solution(request):
    """Switch between different solutions"""
    
    if request.method == 'POST':
        solution_name = request.POST.get('solution_name')
        
        if solution_name:
            request.session['solution_name'] = solution_name
            
            return JsonResponse({
                'success': True,
                'message': f'Switched to solution: {solution_name}'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Solution name required'
            }, status=400)
    
    # Get available solutions
    available_solutions = ['solution1', 'solution2', 'solution3']  # Your logic here
    
    return render(request, 'your_app/switch_solution.html', {
        'solutions': available_solutions
    })
```

### **Step 6: Create Templates**

```html
<!-- your_app/templates/your_app/dashboard.html -->
{% extends 'base.html' %}

{% block content %}
<div class="dashboard">
    <h1>Business Dashboard - {{ solution_name }}</h1>
    
    <!-- KPI Cards -->
    <div class="kpi-cards">
        {% for kpi in kpis %}
        <div class="kpi-card">
            <h3>{{ kpi.name }}</h3>
            <p class="kpi-value">{{ kpi.value }}</p>
            <p class="kpi-change {% if kpi.change > 0 %}positive{% else %}negative{% endif %}">
                {{ kpi.change }}%
            </p>
        </div>
        {% endfor %}
    </div>
    
    <!-- Partners List -->
    <div class="partners-section">
        <h2>Recent Partners</h2>
        <div class="partners-list">
            {% for partner in partners.data %}
            <div class="partner-item">
                <h4>{{ partner.name }}</h4>
                <p>{{ partner.email }}</p>
                <p>{{ partner.phone }}</p>
            </div>
            {% endfor %}
        </div>
    </div>
</div>
{% endblock %}
```

```html
<!-- your_app/templates/your_app/solution_setup.html -->
{% extends 'base.html' %}

{% block content %}
<div class="solution-setup">
    <h1>Setup New Solution</h1>
    
    <form method="post" id="setup-form">
        {% csrf_token %}
        
        <div class="form-group">
            <label for="solution_name">Solution Name:</label>
            <input type="text" id="solution_name" name="solution_name" required>
            <small>Use lowercase, no spaces (e.g., my_enterprise_solution)</small>
        </div>
        
        <div class="form-group">
            <label for="company_name">Company Name:</label>
            <input type="text" id="company_name" name="company_name" required>
        </div>
        
        <div class="form-group">
            <label for="industry">Industry:</label>
            <select id="industry" name="industry" required>
                <option value="">Select Industry</option>
                <option value="technology">Technology</option>
                <option value="manufacturing">Manufacturing</option>
                <option value="services">Services</option>
                <option value="retail">Retail</option>
            </select>
        </div>
        
        <div class="form-group">
            <label for="employee_count">Employee Count:</label>
            <input type="number" id="employee_count" name="employee_count" min="1" required>
        </div>
        
        <button type="submit">Setup Solution</button>
    </form>
</div>

<script>
document.getElementById('setup-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    
    try {
        const response = await fetch('{% url "solution_setup" %}', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert(result.message);
            window.location.href = '{% url "business_dashboard" %}';
        } else {
            alert('Error: ' + result.error);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
});
</script>
{% endblock %}
```

### **Step 7: Add URL Patterns**

```python
# your_app/urls.py

from django.urls import path
from . import views

app_name = 'your_app'

urlpatterns = [
    path('dashboard/', views.business_dashboard, name='business_dashboard'),
    path('setup/', views.solution_setup, name='solution_setup'),
    path('switch/', views.switch_solution, name='switch_solution'),
    path('partner/create/', views.create_partner, name='create_partner'),
]
```

### **Step 8: Create Management Commands**

```python
# your_app/management/commands/setup_solution.py

from django.core.management.base import BaseCommand
from fbs_app.interfaces import FBSInterface

class Command(BaseCommand):
    help = 'Setup a new solution with FBS'

    def add_arguments(self, parser):
        parser.add_argument('solution_name', type=str, help='Name of the solution')
        parser.add_argument('--company-name', type=str, required=True, help='Company name')
        parser.add_argument('--industry', type=str, required=True, help='Industry type')
        parser.add_argument('--employee-count', type=int, default=1, help='Employee count')

    def handle(self, *args, **options):
        solution_name = options['solution_name']
        
        self.stdout.write(f"Setting up solution: {solution_name}")
        
        try:
            # Initialize FBS
            fbs = FBSInterface(solution_name)
            
            # Setup business
            result = fbs.msme.setup_business(
                business_type='services',
                config={
                    'company_name': options['company_name'],
                    'industry': options['industry'],
                    'employee_count': options['employee_count'],
                }
            )
            
            if result['success']:
                self.stdout.write(
                    self.style.SUCCESS(f"Solution {solution_name} setup successfully!")
                )
                self.stdout.write(f"Business ID: {result['data']['business_id']}")
            else:
                self.stdout.write(
                    self.style.ERROR(f"Setup failed: {result.get('message')}")
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error: {str(e)}")
            )
```

## 🔧 Advanced Integration Patterns

### **1. Custom Service Wrapper**

```python
# your_app/services/fbs_wrapper.py

from fbs_app.interfaces import FBSInterface
from typing import Dict, Any, Optional

class FBSServiceWrapper:
    """Wrapper for FBS services with solution-specific logic"""
    
    def __init__(self, solution_name: str):
        self.solution_name = solution_name
        self.fbs = FBSInterface(solution_name)
    
    def get_business_summary(self) -> Dict[str, Any]:
        """Get comprehensive business summary"""
        try:
            dashboard = self.fbs.msme.get_dashboard()
            kpis = self.fbs.msme.calculate_kpis()
            compliance = self.fbs.msme.get_compliance_status()
            
            return {
                'dashboard': dashboard,
                'kpis': kpis,
                'compliance': compliance,
                'solution_name': self.solution_name,
                'status': 'success'
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def create_business_entity(self, entity_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create business entity with validation"""
        
        # Your custom validation logic
        if entity_type == 'partner':
            if not data.get('email'):
                return {'success': False, 'error': 'Email is required'}
            
            # Create in Odoo
            result = self.fbs.odoo.create_record('res.partner', data)
            
            if result['success']:
                # Add custom fields
                self.fbs.fields.set_custom_field(
                    'res.partner',
                    result['data']['id'],
                    'source_solution',
                    self.solution_name,
                    'char'
                )
            
            return result
        
        return {'success': False, 'error': f'Unknown entity type: {entity_type}'}
```

### **2. Middleware Integration**

```python
# your_app/middleware.py

from django.utils.deprecation import MiddlewareMixin
from fbs_app.interfaces import FBSInterface

class FBSSolutionMiddleware(MiddlewareMixin):
    """Middleware to inject FBS solution context"""
    
    def process_request(self, request):
        # Get solution name from various sources
        solution_name = (
            request.GET.get('solution') or
            request.POST.get('solution') or
            request.session.get('solution_name') or
            'default_solution'
        )
        
        # Store in request for easy access
        request.fbs_solution = solution_name
        
        # Initialize FBS interface
        try:
            request.fbs = FBSInterface(solution_name)
        except Exception as e:
            request.fbs = None
            request.fbs_error = str(e)
    
    def process_response(self, request, response):
        # Add solution info to response headers
        if hasattr(request, 'fbs_solution'):
            response['X-FBS-Solution'] = request.fbs_solution
        
        return response
```

### **3. Context Processors**

```python
# your_app/context_processors.py

def fbs_context(request):
    """Add FBS context to all templates"""
    
    context = {
        'fbs_solution': getattr(request, 'fbs_solution', 'default_solution'),
        'fbs_available': hasattr(request, 'fbs') and request.fbs is not None,
    }
    
    if hasattr(request, 'fbs') and request.fbs:
        try:
            # Add basic FBS info to context
            context['fbs_health'] = request.fbs.get_system_health()
        except:
            context['fbs_health'] = {'status': 'error'}
    
    return context
```

## 🧪 Testing Your Integration

### **1. Test Configuration**

```python
# your_app/tests/test_fbs_integration.py

from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch, MagicMock

class FBSIntegrationTest(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.solution_name = 'test_solution'
    
    @patch('your_app.views.FBSInterface')
    def test_business_dashboard(self, mock_fbs):
        """Test business dashboard with FBS integration"""
        
        # Mock FBS interface
        mock_fbs_instance = MagicMock()
        mock_fbs_instance.msme.get_dashboard.return_value = {
            'status': 'success',
            'data': {'revenue': 10000, 'customers': 50}
        }
        mock_fbs_instance.msme.calculate_kpis.return_value = [
            {'name': 'Revenue', 'value': 10000, 'change': 15}
        ]
        mock_fbs_instance.odoo.get_records.return_value = {
            'status': 'success',
            'data': [{'name': 'Test Partner', 'email': 'test@example.com'}]
        }
        mock_fbs.return_value = mock_fbs_instance
        
        # Set session
        session = self.client.session
        session['solution_name'] = self.solution_name
        session.save()
        
        # Make request
        response = self.client.get(reverse('your_app:business_dashboard'))
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Partner')
        self.assertContains(response, 'Revenue')
    
    def test_solution_setup(self):
        """Test solution setup process"""
        
        response = self.client.post(reverse('your_app:solution_setup'), {
            'solution_name': 'new_solution',
            'company_name': 'New Company',
            'industry': 'technology',
            'employee_count': 25
        })
        
        self.assertEqual(response.status_code, 200)
        # Add more assertions based on your implementation
```

### **2. Test Database Setup**

```python
# your_app/tests/conftest.py

import pytest
from django.conf import settings

@pytest.fixture(scope='session')
def django_db_setup():
    """Setup test databases"""
    settings.DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        },
        'djo_test_solution_db': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        },
        'fbs_test_solution_db': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }

@pytest.fixture
def fbs_interface():
    """Provide FBS interface for testing"""
    from fbs_app.interfaces import FBSInterface
    return FBSInterface('test_solution')
```

## 🚨 Troubleshooting

### **Common Issues**

1. **Django Settings Not Configured**
   ```python
   # ❌ Error: Requested setting INSTALLED_APPS, but settings are not configured
   # ✅ Solution: Ensure Django is configured before importing FBS
   
   import os
   import django
   os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')
   django.setup()
   ```

2. **Database Connection Issues**
   ```python
   # ❌ Error: connection to server at "localhost" failed
   # ✅ Solution: Check environment variables and database settings
   
   # Ensure these are set:
   # FBS_DB_HOST, FBS_DB_PORT, FBS_DB_USER, FBS_DB_PASSWORD
   # ODOO_BASE_URL, ODOO_USER, ODOO_PASSWORD
   ```

3. **Model Import Errors**
   ```python
   # ❌ Error: cannot import name 'MSMEBusiness' from 'fbs_app.models'
   # ✅ Solution: Use FBSInterface, not direct model imports
   
   from fbs_app.interfaces import FBSInterface
   fbs = FBSInterface('solution_name')
   ```

4. **Solution Not Found**
   ```python
   # ❌ Error: Solution database not found
   # ✅ Solution: Ensure solution is properly initialized
   
   # Check if solution exists
   fbs = FBSInterface('solution_name')
   health = fbs.get_system_health()
   
   if health['status'] == 'error':
       # Setup solution first
       fbs.msme.setup_business('services', {...})
   ```

## 📚 Next Steps

### **1. Explore FBS Capabilities**
- Read the [API Reference](API_REFERENCE.md)
- Check the [Developer Guide](DEVELOPER_GUIDE.md)
- Review the [Odoo Integration Guide](ODOO_INTEGRATION.md)

### **2. Build Your Solution**
- Create custom business logic
- Design user interfaces
- Implement workflow processes
- Add custom reporting

### **3. Test and Deploy**
- Run comprehensive tests
- Performance testing
- Security review
- Production deployment

---

**FBS Suite v2.0.4** - Ready for embedding! 🚀

*This guide provides practical, step-by-step instructions for integrating FBS into your Django solutions. Follow the patterns and examples to build robust, scalable business applications.*
