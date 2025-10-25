# Fayvad Rentals - Property Management System

**A complete rental property management solution built with Django**

[![Django](https://img.shields.io/badge/Django-5.1.2-green.svg)](https://djangoproject.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7-red.svg)](https://redis.io/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com/)

## 🚀 Overview

Fayvad Rentals is a comprehensive property management system that streamlines rental operations for property managers and owners. Built as a pure Django application with modern web technologies, it provides all the tools needed to manage properties, tenants, payments, maintenance, and reporting.

## ✨ Features

### 🏢 Property Management
- **Multi-location support** - Manage properties across different locations
- **Room/unit tracking** - Detailed room management with amenities and pricing
- **Property analytics** - Occupancy rates, revenue tracking, and performance metrics

### 👥 Tenant Management
- **Complete tenant profiles** - Contact information, emergency contacts, rental history
- **Tenant portal** - Self-service access for payments, maintenance requests, and documents
- **Lease agreements** - Digital contract management with e-signatures

### 💰 Payment Processing
- **Automated rent collection** - Scheduled payments and reminders
- **Multi-payment methods** - M-Pesa, bank transfers, cash payments
- **Payment tracking** - Complete audit trail with verification workflows
- **Financial reporting** - Revenue analysis and payment history

### 🔧 Maintenance Management
- **Maintenance requests** - Tenant-submitted issues with photo attachments
- **Workflow automation** - Assign technicians, track progress, approval processes
- **Priority management** - Urgent, high, medium, low priority classification
- **Cost tracking** - Maintenance expenses and budget management

### 📊 Reporting & Analytics
- **Comprehensive dashboards** - Real-time insights and KPIs
- **Financial reports** - Revenue, expenses, profitability analysis
- **Occupancy reports** - Vacancy rates and leasing performance
- **Custom reporting** - Exportable reports in multiple formats

### 🔐 Security & Access Control
- **Role-based permissions** - Manager, caretaker, cleaner, tenant roles
- **Audit logging** - Complete activity tracking and compliance
- **Secure authentication** - Modern security practices
- **Data encryption** - Sensitive data protection

## 🏗️ Architecture

### Tech Stack
- **Backend**: Django 5.1.2 (Python web framework)
- **Database**: PostgreSQL 15 (Relational database)
- **Cache**: Redis 7 (Session and cache storage)
- **Frontend**: Django Templates (Server-side rendering)
- **Styling**: TailwindCSS (CDN delivery)
- **JavaScript**: Vanilla JavaScript (Minimal client-side interactions)

### Project Structure
```
fayvad_rentals_django/
├── accounts/           # User authentication & profiles
├── dashboard/          # Analytics & reporting dashboard
├── tenants/            # Tenant management
├── properties/         # Property & room management
├── rentals/            # Lease agreements
├── payments/           # Payment processing & verification
├── maintenance/        # Maintenance requests & workflows
├── documents/          # Document management
├── reports/            # Report generation
├── workflows/          # Business process automation
├── core_services/      # Shared business logic
├── templates/          # Django HTML templates
├── static/            # Static assets (CSS, JS, images)
└── manage.py          # Django management script
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd fayvad-rentals
   ```

2. **Environment Setup**
   ```bash
   # Copy and configure environment variables
   cp .env.example .env
   # Edit .env with your database credentials
   ```

3. **Start with Docker**
   ```bash
   docker-compose up -d
   ```

4. **Run Migrations**
   ```bash
   docker-compose exec django-web python manage.py migrate
   ```

5. **Create Superuser**
   ```bash
   docker-compose exec django-web python manage.py createsuperuser
   ```

6. **Access the Application**
   - Main application: http://localhost:8000
   - Admin panel: http://localhost:8000/admin

### Manual Installation (Development)

1. **Install Dependencies**
   ```bash
   cd fayvad_rentals_django
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Database Setup**
   ```bash
   # Install PostgreSQL and create database
   createdb fayvad_rental_db
   ```

3. **Run Development Server**
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

## 📖 Usage

### For Property Managers
1. **Setup Properties** - Add locations, buildings, and rooms
2. **Onboard Tenants** - Create tenant profiles and assign rooms
3. **Manage Leases** - Create rental agreements with terms
4. **Monitor Payments** - Track rent collection and verify payments
5. **Handle Maintenance** - Process tenant requests and track resolution
6. **Generate Reports** - Analyze performance and financials

### For Tenants
1. **Access Portal** - Login to tenant dashboard
2. **View Profile** - Update personal information
3. **Make Payments** - Submit rent payments with verification
4. **Submit Requests** - Report maintenance issues with photos
5. **View Documents** - Access lease agreements and receipts
6. **Track History** - View payment and maintenance history

## 🔧 Configuration

### Environment Variables
```bash
DEBUG=true
SECRET_KEY=your-secret-key
DB_NAME=fayvad_rental_db
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432
REDIS_URL=redis://localhost:6379/0
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Key Settings
- **Database**: PostgreSQL with connection pooling
- **Caching**: Redis for sessions and expensive queries
- **Static Files**: Served via Django in development, Nginx in production
- **Media Files**: Stored locally in development, cloud storage in production

## 🧪 Testing

```bash
# Run Django tests
cd fayvad_rentals_django
python manage.py test

# Run with coverage
coverage run manage.py test
coverage report
```

## 🚀 Deployment

### Production with Docker
```bash
# Build and deploy
docker-compose -f docker-compose.prod.yml up -d

# Scale application
docker-compose up -d --scale django-web=3
```

### Production with Gunicorn
```bash
# Install production dependencies
pip install gunicorn psycopg2-binary

# Run with Gunicorn
gunicorn fayvad_rentals.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is proprietary software. All rights reserved.

## 📞 Support

For support and questions:
- **Email**: services@rental.fayvad.com
- **Phone**: +254 712 104 734
- **Address**: P.O. Box 1762-00900, Kiambu, Kenya

## 🙏 Acknowledgments

- Django Framework - The web framework that makes this possible
- TailwindCSS - Beautiful, responsive styling
- PostgreSQL - Reliable data storage
- Redis - High-performance caching

---

**Fayvad Rentals** - Modernizing property management, one rental at a time.
