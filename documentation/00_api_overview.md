# FBS API Overview 📚

**Copyright © 2025 Fayvad Digital. All rights reserved.**

## 🎯 **API Overview**

The FBS (Fayvad Business Suite) API provides comprehensive business management capabilities for MSMEs (Micro, Small, and Medium Enterprises) with integrated Odoo ERP functionality.

### **Base URL**
```
https://api.fayvad.com/api/
```

### **API Version**
- **Current Version**: v1
- **Stability**: Production Ready
- **Authentication**: Handshake Authentication Required

## 📊 **API Categories**

### **1. Core Operations** (`/api/v1/`)
- **Generic Model Operations**: CRUD operations for any Odoo model
- **Database Management**: Multi-tenant database operations
- **Token Management**: Authentication token handling

### **2. MSME Features** (`/api/msme/`)
- **Business Setup**: MSME business configuration
- **KPI Management**: Key performance indicators
- **Compliance**: Regulatory compliance management
- **Marketing**: Campaign management

### **3. Client Onboarding** (`/api/onboarding/`)
- **Business Setup**: Guided business configuration
- **Template Management**: Pre-configured business templates
- **Demo Data**: Sample data import

### **4. Business Intelligence** (`/api/bi/`)
- **Analytics**: Data analysis and insights
- **Reports**: Sales, inventory, and financial reports
- **Dashboards**: Interactive business dashboards
- **KPI Summary**: Key performance metrics

### **5. Simplified Workflows** (`/api/workflows/simple/`)
- **Approval Workflows**: Simple approval processes
- **Customer Onboarding**: Customer setup workflows
- **Order Processing**: Order management workflows
- **Payment Collection**: Payment processing workflows
- **Inventory Management**: Stock management workflows

### **6. Notifications** (`/api/notifications/`)
- **Alerts**: Business alerts and notifications
- **Cash Flow**: Cash flow monitoring
- **Payment Reminders**: Payment due notifications
- **Inventory Alerts**: Stock level notifications
- **Compliance Deadlines**: Regulatory deadline reminders
- **Customer Follow-ups**: Customer engagement reminders

### **7. Compliance Management** (`/api/compliance/`)
- **Tax Calculations**: Basic tax computation
- **Payroll Basics**: Simple payroll processing
- **Audit Trails**: Compliance audit tracking
- **Regulatory Reports**: Compliance reporting
- **Deadline Management**: Regulatory deadline tracking

### **8. Simple Accounting** (`/api/accounting/`)
- **Cash Basis Accounting**: Simple cash-based accounting
- **Basic Ledger**: General ledger management
- **Income/Expense Tracking**: Financial transaction tracking
- **Basic Reports**: Simple financial reporting
- **Tax Calculations**: Basic tax computations

### **9. Analytics & Dashboards** (`/api/analytics/`)
- **Business Overview**: High-level business metrics
- **Daily Cash Position**: Daily financial position
- **Sales Summary**: Sales performance analytics
- **Customer Activity**: Customer engagement metrics
- **Profit Tracking**: Profitability analysis
- **Inventory Analytics**: Stock performance metrics
- **Performance Metrics**: Overall business performance

### **10. System Management** (`/api/`)
- **Health Checks**: System health monitoring
- **Solution Management**: Multi-tenant solution handling
- **Profile Management**: System profiling and discovery

## 🔐 **Authentication**

All API endpoints require **Handshake Authentication**:

1. **Create Handshake**: `POST /api/auth/handshake/create/`
2. **Include Token**: Add `Authorization: Bearer <handshake_token>` header
3. **Database Context**: Handshake includes database context

### **Authentication Flow**
```
1. Create Handshake → Get handshake_token
2. Include token in all requests
3. Token includes database context
4. Automatic database routing
```

## 📋 **Request/Response Format**

### **Standard Request Format**
```json
{
  "solution_name": "business_name",
  "data": {
    // Request-specific data
  }
}
```

### **Standard Response Format**
```json
{
  "success": true,
  "data": {
    // Response data
  },
  "message": "Operation completed successfully"
}
```

### **Error Response Format**
```json
{
  "success": false,
  "error": "Error description",
  "error_code": "ERROR_CODE",
  "details": {
    // Additional error details
  }
}
```

## 🚀 **Quick Start**

### **1. Create Handshake**
```bash
curl -X POST https://api.fayvad.com/api/auth/handshake/create/ \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "your_api_key",
    "system_name": "your_system",
    "database_name": "your_database"
  }'
```

### **2. Use API Endpoints**
```bash
curl -X GET https://api.fayvad.com/api/msme/dashboard/ \
  -H "Authorization: Bearer <handshake_token>" \
  -H "Content-Type: application/json"
```

## 📈 **Rate Limiting**

- **Standard**: 1000 requests per hour
- **Burst**: 100 requests per minute
- **Headers**: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

## 🔧 **Error Handling**

- **400**: Bad Request - Invalid parameters
- **401**: Unauthorized - Authentication required
- **403**: Forbidden - Insufficient permissions
- **404**: Not Found - Resource not found
- **429**: Too Many Requests - Rate limit exceeded
- **500**: Internal Server Error - Server error

## 📚 **Documentation Structure**

1. **[01_core_operations.md](01_core_operations.md)** - Core API operations
2. **[02_msme_features.md](02_msme_features.md)** - MSME-specific features
3. **[03_onboarding.md](03_onboarding.md)** - Client onboarding
4. **[04_business_intelligence.md](04_business_intelligence.md)** - BI and analytics
5. **[05_workflows.md](05_workflows.md)** - Simplified workflows
6. **[06_notifications.md](06_notifications.md)** - Notification system
7. **[07_compliance.md](07_compliance.md)** - Compliance management
8. **[08_accounting.md](08_accounting.md)** - Simple accounting
9. **[09_analytics.md](09_analytics.md)** - Analytics and dashboards
10. **[10_authentication.md](10_authentication.md)** - Authentication details
11. **[11_error_handling.md](11_error_handling.md)** - Error handling guide

## 🎯 **Use Cases**

### **MSME Business Setup**
1. **Onboarding**: Use `/api/onboarding/` endpoints
2. **MSME Configuration**: Use `/api/msme/` endpoints
3. **Dashboard Setup**: Use `/api/analytics/` endpoints

### **Daily Operations**
1. **Workflows**: Use `/api/workflows/simple/` endpoints
2. **Notifications**: Use `/api/notifications/` endpoints
3. **Accounting**: Use `/api/accounting/` endpoints

### **Compliance & Reporting**
1. **Compliance**: Use `/api/compliance/` endpoints
2. **Reports**: Use `/api/bi/` endpoints
3. **Analytics**: Use `/api/analytics/` endpoints

## 🔗 **Related Documentation**

- **[API Endpoints Complete](API_ENDPOINTS_COMPLETE.md)** - Complete endpoint reference
- **[Codebase Review](CODEBASE_REVIEW_2025.md)** - Technical implementation details
- **[MSME Best Practices](MSME_BEST_PRACTICES_REVIEW.md)** - MSME-specific guidance 