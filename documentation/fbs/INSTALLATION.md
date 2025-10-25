# FBS Installation Guide

## Overview

This guide covers the installation and configuration of the **FBS (Fayvad Business Suite)** ecosystem in your Django project. FBS provides Odoo-driven business management capabilities through three core apps.

## Prerequisites

- **Python 3.8+**
- **Django 3.2+**
- **PostgreSQL 12+** (recommended) or SQLite
- **Odoo ERP system** (for full functionality)
- **Git**

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/kuriadn/fbs.git
cd fbs
```

### 2. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .
```

### 3. Add to Django Settings

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

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # FBS Middleware
    'fbs_app.middleware.DatabaseRoutingMiddleware',
    'fbs_app.middleware.RequestLoggingMiddleware',
]
```

### 4. Configure FBS

```python
# settings.py
FBS_APP = {
    # Odoo Integration
    'ODOO_BASE_URL': 'http://your-odoo-server:8069',
    'ODOO_TIMEOUT': 30,
    'ODOO_MAX_RETRIES': 3,
    'DATABASE_USER': 'your_odoo_user',
    'DATABASE_PASSWORD': 'your_odoo_password',
    
    # Features
    'ENABLE_MSME_FEATURES': True,
    'ENABLE_BI_FEATURES': True,
    'ENABLE_WORKFLOW_FEATURES': True,
    'ENABLE_COMPLIANCE_FEATURES': True,
    'ENABLE_ACCOUNTING_FEATURES': True,
    
    # Cache
    'CACHE_ENABLED': True,
    'CACHE_TIMEOUT': 300,
}

# DMS Configuration
FBS_DMS = {
    'UPLOAD_PATH': 'documents/',
    'MAX_FILE_SIZE': 10485760,  # 10MB
    'ALLOWED_EXTENSIONS': ['.pdf', '.doc', '.docx', '.xls', '.xlsx'],
    'ENABLE_VERSIONING': True,
    'ENABLE_WORKFLOWS': True,
}

# License Manager Configuration
FBS_LICENSE_MANAGER = {
    'ENABLE_LICENSING': True,
    'LICENSE_TYPE': 'professional',
    'FEATURE_LIMITS': {
        'msme_businesses': 10,
        'workflows': 50,
        'reports': 1000,
        'users': 25,
        'documents': 5000,
        'storage_gb': 100
    }
}
```

### 5. Database Configuration

```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'fbs_system_db',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    },
    'licensing': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'fbs_licensing_db',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Database Router
DATABASE_ROUTERS = ['fbs_app.routers.FBSDatabaseRouter']
```

### 6. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create Superuser

```bash
python manage.py createsuperuser
```

## Configuration

### Environment Variables

Create a `.env` file in your project root:

```bash
# Django
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=fbs_system_db
DB_USER=your_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# Odoo
ODOO_BASE_URL=http://localhost:8069
ODOO_DATABASE_USER=your_odoo_user
ODOO_DATABASE_PASSWORD=your_odoo_password
```

### Odoo Configuration

Ensure your Odoo system is accessible and has the required models:

- `res.partner` - for company/contact management
- `ir.attachment` - for document storage
- `res.company` - for company information

## Testing Installation

### 1. Basic Health Check

```python
from fbs_app.interfaces import FBSInterface

# Initialize interface
fbs = FBSInterface('test_solution')

# Check system health
health = fbs.get_system_health()
print(f"System status: {health['status']}")

# Check Odoo availability
odoo_available = fbs.is_odoo_available()
print(f"Odoo available: {odoo_available}")
```

### 2. Test Odoo Integration

```python
# Discover Odoo models
models = fbs.odoo.discover_models()
print(f"Available models: {len(models['data'])}")

# Test record retrieval
partners = fbs.odoo.get_records('res.partner', limit=5)
print(f"Found {len(partners['data'])} partners")
```

### 3. Test Virtual Fields

```python
# Set custom field
result = fbs.fields.set_custom_field(
    'res.partner', 1, 'test_field', 'test_value', 'char'
)
print(f"Field set: {result['success']}")

# Get custom field
field_data = fbs.fields.get_custom_field('res.partner', 1, 'test_field')
print(f"Field value: {field_data['data']}")
```

## Troubleshooting

### Common Issues

#### 1. Import Errors

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall in development mode
pip install -e .
```

#### 2. Database Connection Issues

```bash
# Check database settings
python manage.py dbshell

# Verify migrations
python manage.py showmigrations
```

#### 3. Odoo Connection Issues

```python
# Test Odoo connectivity
from fbs_app.services.odoo_client import OdooClient

client = OdooClient('test_solution')
available = client.is_available()
print(f"Odoo available: {available}")
```

#### 4. Permission Issues

```bash
# Check file permissions
chmod -R 755 fbs_app/
chmod -R 755 fbs_dms/
chmod -R 755 fbs_license_manager/

# Check database permissions
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE fbs_system_db TO your_user;"
```

## Next Steps

After successful installation:

1. **Read the [Integration Guide](INTEGRATION.md)** - Learn how to embed FBS in your projects
2. **Check the [Developer Guide](DEVELOPER_GUIDE.md)** - Understand service interfaces
3. **Review [Odoo Integration](ODOO_INTEGRATION.md)** - Master Odoo + Virtual Fields
4. **Explore [API Reference](API_REFERENCE.md)** - Complete interface documentation

## Support

For installation issues:

- Check the [troubleshooting section](#troubleshooting)
- Review [reported bugs](reported%20bugs/) for known issues
- Create an issue in the GitHub repository
- Contact the development team

---

**FBS Installation Complete!** 🎉

Your Django project now has access to Odoo-driven business management capabilities through FBS Virtual Fields technology.
