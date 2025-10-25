# MSME Features API 🏢

**Copyright © 2025 Fayvad Digital. All rights reserved.**

## 🎯 **Overview**

MSME (Micro, Small, and Medium Enterprises) features provide specialized business management capabilities tailored for small businesses, including setup wizards, KPI tracking, compliance management, and marketing tools.

## 🔐 **Authentication**

All endpoints require **Handshake Authentication**:
```bash
Authorization: Bearer <handshake_token>
```

## 🚀 **Business Setup & Configuration**

### **Setup MSME Business**
```http
POST /api/msme/setup/
```

**Description**: Initialize MSME business configuration

**Request Body**:
```json
{
  "solution_name": "my_business",
  "business_type": "retail",
  "business_name": "My Retail Store",
  "industry": "retail",
  "employee_count": 10,
  "annual_revenue": 500000,
  "modules": ["sale", "purchase", "inventory"],
  "demo_data": true
}
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "setup_id": "setup_123",
    "business_name": "My Retail Store",
    "business_type": "retail",
    "status": "configuring",
    "next_steps": [
      "Configure chart of accounts",
      "Set up product categories",
      "Import initial inventory"
    ],
    "estimated_completion": "2 hours"
  },
  "message": "MSME business setup initiated successfully"
}
```

### **Get MSME Dashboard**
```http
GET /api/msme/dashboard/
```

**Description**: Get comprehensive MSME business dashboard

**Parameters**:
- `solution_name` (required): Business solution name
- `period` (optional): Time period (day, week, month, quarter, year)

**Example Response**:
```json
{
  "success": true,
  "data": {
    "business_overview": {
      "business_name": "My Retail Store",
      "business_type": "retail",
      "status": "active",
      "setup_completion": 85
    },
    "key_metrics": {
      "total_sales": 125000,
      "total_customers": 45,
      "total_products": 150,
      "cash_balance": 25000
    },
    "recent_activities": [
      {
        "type": "sale",
        "description": "New sale: $1,200",
        "timestamp": "2025-01-01T12:00:00Z"
      }
    ],
    "alerts": [
      {
        "type": "low_stock",
        "message": "5 products running low on stock",
        "severity": "medium"
      }
    ]
  }
}
```

### **Get Setup Wizards**
```http
GET /api/msme/wizards/
```

**Description**: Get available setup wizards for business configuration

**Example Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": "chart_of_accounts",
      "name": "Chart of Accounts Setup",
      "description": "Configure your business chart of accounts",
      "estimated_time": "30 minutes",
      "required": true,
      "status": "pending"
    },
    {
      "id": "product_categories",
      "name": "Product Categories",
      "description": "Set up your product categories",
      "estimated_time": "15 minutes",
      "required": true,
      "status": "completed"
    }
  ]
}
```

### **Get Templates**
```http
GET /api/msme/templates/
```

**Description**: Get pre-configured business templates

**Parameters**:
- `business_type` (optional): Filter by business type
- `template_type` (optional): Filter by template type

**Example Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": "retail_basic",
      "name": "Basic Retail Template",
      "business_type": "retail",
      "description": "Standard retail business setup",
      "modules": ["sale", "purchase", "inventory"],
      "chart_of_accounts": "retail_coa",
      "product_categories": ["electronics", "clothing", "home"],
      "demo_data": true
    }
  ]
}
```

## 📊 **KPI Management**

### **Calculate KPIs**
```http
POST /api/msme/kpis/calculate/
```

**Description**: Calculate key performance indicators

**Request Body**:
```json
{
  "solution_name": "my_business",
  "kpi_types": ["cash_flow", "sales", "inventory", "customers"],
  "period": "month",
  "date_from": "2025-01-01",
  "date_to": "2025-01-31"
}
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "cash_flow": {
      "current_balance": 25000,
      "monthly_income": 125000,
      "monthly_expenses": 95000,
      "net_cash_flow": 30000,
      "trend": "increasing"
    },
    "sales": {
      "total_sales": 125000,
      "sales_growth": 15.5,
      "average_order_value": 850,
      "top_products": [
        {"name": "Product A", "sales": 15000},
        {"name": "Product B", "sales": 12000}
      ]
    },
    "inventory": {
      "total_items": 150,
      "low_stock_items": 5,
      "out_of_stock_items": 2,
      "inventory_value": 45000
    },
    "customers": {
      "total_customers": 45,
      "new_customers": 8,
      "repeat_customers": 37,
      "customer_satisfaction": 4.2
    }
  }
}
```

### **Get KPI History**
```http
GET /api/msme/kpis/history/
```

**Description**: Get historical KPI data

**Parameters**:
- `solution_name` (required): Business solution name
- `kpi_type` (optional): Specific KPI type
- `period` (optional): Time period
- `limit` (optional): Number of records (default: 30)

**Example Response**:
```json
{
  "success": true,
  "data": [
    {
      "date": "2025-01-01",
      "cash_flow": 25000,
      "sales": 125000,
      "customers": 45,
      "inventory_value": 45000
    },
    {
      "date": "2024-12-01",
      "cash_flow": 22000,
      "sales": 110000,
      "customers": 42,
      "inventory_value": 42000
    }
  ]
}
```

## 📋 **Compliance Management**

### **Get Compliance Tasks**
```http
GET /api/msme/compliance/tasks/
```

**Description**: Get compliance tasks and deadlines

**Parameters**:
- `solution_name` (required): Business solution name
- `status` (optional): Filter by status (pending, completed, overdue)
- `compliance_type` (optional): Filter by compliance type

**Example Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": "task_1",
      "title": "Monthly Tax Filing",
      "description": "File monthly sales tax return",
      "compliance_type": "tax",
      "deadline": "2025-01-31T23:59:59Z",
      "status": "pending",
      "priority": "high",
      "estimated_time": "2 hours"
    },
    {
      "id": "task_2",
      "title": "Annual Business License Renewal",
      "description": "Renew business operating license",
      "compliance_type": "licensing",
      "deadline": "2025-03-31T23:59:59Z",
      "status": "pending",
      "priority": "medium",
      "estimated_time": "1 hour"
    }
  ]
}
```

### **Create Compliance Task**
```http
POST /api/msme/compliance/create/
```

**Description**: Create a new compliance task

**Request Body**:
```json
{
  "solution_name": "my_business",
  "title": "Quarterly VAT Return",
  "description": "File quarterly VAT return",
  "compliance_type": "tax",
  "deadline": "2025-03-31T23:59:59Z",
  "priority": "high",
  "estimated_time": "3 hours",
  "reminder_days": 7
}
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "task_id": "task_3",
    "title": "Quarterly VAT Return",
    "status": "pending",
    "created_at": "2025-01-01T12:00:00Z"
  },
  "message": "Compliance task created successfully"
}
```

## 📢 **Marketing Management**

### **Get Marketing Campaigns**
```http
GET /api/msme/marketing/campaigns/
```

**Description**: Get marketing campaigns

**Parameters**:
- `solution_name` (required): Business solution name
- `status` (optional): Filter by status (active, completed, draft)
- `campaign_type` (optional): Filter by campaign type

**Example Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": "campaign_1",
      "name": "Holiday Sale Campaign",
      "description": "End of year holiday sale promotion",
      "campaign_type": "email",
      "status": "active",
      "start_date": "2025-01-01T00:00:00Z",
      "end_date": "2025-01-31T23:59:59Z",
      "target_audience": "existing_customers",
      "budget": 5000,
      "spent": 3200,
      "results": {
        "emails_sent": 1000,
        "opens": 450,
        "clicks": 120,
        "conversions": 25
      }
    }
  ]
}
```

### **Create Marketing Campaign**
```http
POST /api/msme/marketing/create/
```

**Description**: Create a new marketing campaign

**Request Body**:
```json
{
  "solution_name": "my_business",
  "name": "New Product Launch",
  "description": "Launch campaign for new product line",
  "campaign_type": "email",
  "start_date": "2025-02-01T00:00:00Z",
  "end_date": "2025-02-28T23:59:59Z",
  "target_audience": "all_customers",
  "budget": 3000,
  "message": "Introducing our new product line with 20% discount!",
  "reminder_frequency": "weekly"
}
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "campaign_id": "campaign_2",
    "name": "New Product Launch",
    "status": "draft",
    "created_at": "2025-01-01T12:00:00Z",
    "estimated_reach": 500
  },
  "message": "Marketing campaign created successfully"
}
```

## 🔧 **Error Handling**

### **Common Error Codes**

| Code | Description | Resolution |
|------|-------------|------------|
| `400` | Bad Request | Check request parameters |
| `401` | Unauthorized | Verify authentication token |
| `403` | Forbidden | Check user permissions |
| `404` | Not Found | Verify business solution exists |
| `429` | Rate Limited | Wait and retry |
| `500` | Server Error | Contact support |

### **Error Response Format**
```json
{
  "success": false,
  "error": "Error description",
  "error_code": "ERROR_CODE",
  "details": {
    "field": "Additional error details"
  }
}
```

## 📈 **Rate Limiting**

- **Standard**: 1000 requests per hour
- **Burst**: 100 requests per minute
- **Headers**: 
  - `X-RateLimit-Limit`: Request limit
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Reset timestamp

## 🎯 **Use Cases**

### **New Business Setup**
1. **Setup Business**: Use `POST /api/msme/setup/`
2. **Configure Templates**: Use `GET /api/msme/templates/`
3. **Run Setup Wizards**: Use `GET /api/msme/wizards/`
4. **Monitor Dashboard**: Use `GET /api/msme/dashboard/`

### **Daily Operations**
1. **Track KPIs**: Use `POST /api/msme/kpis/calculate/`
2. **Monitor Compliance**: Use `GET /api/msme/compliance/tasks/`
3. **Manage Marketing**: Use `GET /api/msme/marketing/campaigns/`

### **Business Growth**
1. **Analyze Performance**: Use KPI history endpoints
2. **Plan Marketing**: Use marketing campaign endpoints
3. **Ensure Compliance**: Use compliance task endpoints

## 🔗 **Related Documentation**

- **[Core Operations](01_core_operations.md)** - Core API operations
- **[Onboarding](03_onboarding.md)** - Client onboarding process
- **[Analytics](09_analytics.md)** - Business analytics and dashboards
- **[Authentication](10_authentication.md)** - Authentication details 