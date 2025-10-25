# Fayvad Rentals - Django Application

**Modern rental property management system** built with Django 5.1.2, direct FBS integration, and production-ready Docker deployment.

## 🚀 Latest Stable Versions (September 2025)

- **Django**: 5.1.2 (latest LTS)
- **Python**: 3.12 (latest stable)
- **PostgreSQL**: 15+ (recommended)
- **Redis**: 7.4 (latest stable)
- **Docker**: 24+ (with Compose v2.24+)

## ✨ Key Features

### 🎯 **Pure Django Architecture**
- Direct database operations (no external API overhead)
- Enterprise business logic in Django models and services
- Automatic tenant data isolation
- Optimized ORM queries

### 🏗️ **Modern Django Architecture**
- **Templates + VanillaJS**: Replaced React complexity with maintainable alternatives
- **REST API**: Full Django REST Framework integration
- **Custom User Model**: Extended authentication system
- **Multi-tenant Ready**: Database-level tenant isolation

### 🐳 **Production-Ready Deployment**
- **Multi-stage Docker builds** for optimized images
- **Health checks** and monitoring
- **Security hardened** containers
- **Scalable architecture** with Redis caching

## 📋 Prerequisites

- Docker 24+ with Docker Compose v2.24+
- PostgreSQL 15+ database
- Redis 7.4+ for caching

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <repository>
cd fayvad_rentals_django
```

### 2. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit with your database credentials
nano .env
```

### 3. Deploy with Docker

```bash
# One-command deployment
./deploy.sh
```

Or manually:

```bash
# Build and start services
docker compose build
docker compose up -d

# Run migrations
docker compose run --rm web python manage.py migrate

# Create superuser
docker compose run --rm web python manage.py createsuperuser

# Collect static files
docker compose run --rm web python manage.py collectstatic --noinput
```

### 4. Access Application

- **Application**: http://localhost:8000
- **Django Admin**: http://localhost:8000/admin/
- **API Documentation**: http://localhost:8000/api/schema/

## 🏛️ Architecture Overview

```
fayvad_rentals_django/
├── 📁 accounts/           # Custom user authentication
├── 📁 tenants/            # Tenant management (FBS integrated)
├── 📁 properties/         # Property management
├── 📁 payments/           # Payment processing
├── 📁 maintenance/        # Maintenance requests
├── 📁 dashboard/          # Business intelligence
├── 📁 fbs_integration/    # Direct FBS service integration
├── 📁 templates/          # Django templates + VanillaJS
├── 📁 static/             # CSS, JS, images
├── 🐳 Dockerfile          # Multi-stage production build
├── 🐳 docker-compose.yml  # Production deployment
└── 🚀 deploy.sh           # Automated deployment
```

## 🔧 Configuration

### Database Setup

The application uses a single database for the rental management system:

| **Database** | **Purpose** | **Default Name** |
|-------------|-------------|------------------|
| **Rental DB** | All application data | `fayvad_rental_db` |

**Optional**: For inventory management, use a separate database: `fayvad_inventory_db`

#### Database Scripts

```bash
# Create/reset database
python recreate_db.py

# Setup database tables and indexes
python setup_db.py

# Check database connectivity
python check_db.py
```

### Environment Variables

```bash
# Django Core
DEBUG=False
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,yourdomain.com

# Database
DATABASE_URL=postgresql://user:pass@host:5432/fayvad_rental_db

# Redis Cache
REDIS_URL=redis://redis:6379/0
```

## 📊 API Endpoints

### Core Modules

- **Authentication**: `/accounts/login/`, `/accounts/logout/`
- **Tenants**: `/tenants/`, `/tenants/<id>/`
- **Properties**: `/properties/`, `/properties/<id>/`
- **Payments**: `/payments/`, `/payments/<id>/`
- **Rentals**: `/rentals/`, `/rentals/<id>/`
- **Maintenance**: `/maintenance/`, `/maintenance/<id>/`

## 🛠️ Development

### Local Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### Testing

```bash
# Run all tests
python manage.py test

# Run with coverage
coverage run manage.py test
coverage report
```

### Code Quality

```bash
# Lint code
flake8 .

# Format code
black .

# Type checking
mypy .
```

## 🚀 Deployment Options

### Development
```bash
docker compose up -d
```

### Production
```bash
docker compose --profile production up -d
```

### Scaling
```bash
# Scale web service
docker compose up -d --scale web=3

# Use load balancer
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 🔒 Security Features

- **Non-root containers** for security
- **Secret management** via environment variables
- **CSRF protection** on all forms
- **SQL injection prevention** via Django ORM
- **XSS protection** via template escaping
- **HTTPS enforcement** in production

## 📈 Performance Optimizations

- **Redis caching** for expensive operations
- **Database query optimization** with select_related/prefetch_related
- **Static file serving** via WhiteNoise
- **Gunicorn workers** for concurrent requests
- **Health checks** for container orchestration

## 🔄 Migration from FastAPI

This Django application **preserves 100% of existing functionality** while providing:

| **Aspect** | **FastAPI + React** | **Django + Templates** |
|------------|-------------------|----------------------|
| **FBS Integration** | Async service layers | Direct method calls |
| **Code Complexity** | 33K+ tokens | ~5K tokens (**85% reduction**) |
| **HTTP Calls** | API → Frontend | Server-side rendering |
| **Deployment** | Multi-container | Single optimized container |
| **SEO** | Client-side rendering | Server-side rendering |
| **Performance** | Async overhead | Synchronous efficiency |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: See `/docs/` directory
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions

---

**Built with ❤️ for modern property management**
