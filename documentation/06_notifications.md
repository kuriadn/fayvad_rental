# Notifications API 🔔

**Copyright © 2025 Fayvad Digital. All rights reserved.**

## 🎯 **Overview**

Notifications provide MSME-specific alerting and reminder capabilities for cash flow monitoring, payment reminders, inventory alerts, compliance deadlines, and customer follow-ups.

## 🔐 **Authentication**

All endpoints require **Handshake Authentication**:
```bash
Authorization: Bearer <handshake_token>
```

## 🚨 **MSME Alerts**

### **Get MSME Alerts**
```http
GET /api/notifications/alerts/
```

**Description**: Get all MSME alerts for the business

**Parameters**:
- `solution_name` (required): Business solution name
- `alert_type` (optional): Filter by alert type
- `severity` (optional): Filter by severity (low, medium, high, critical)
- `status` (optional): Filter by status (active, resolved, dismissed)

**Example Response**:
```json
{
  "success": true,
  "data": [
    {
      "alert_id": "alert_001",
      "alert_type": "cash_flow",
      "title": "Low Cash Balance Alert",
      "message": "Cash balance is below minimum threshold",
      "severity": "high",
      "status": "active",
      "current_value": 5000,
      "threshold": 10000,
      "created_at": "2025-01-01T10:00:00Z",
      "action_required": true,
      "action_url": "/accounting/cash-position"
    },
    {
      "alert_id": "alert_002",
      "alert_type": "inventory",
      "title": "Low Stock Alert",
      "message": "5 products running low on stock",
      "severity": "medium",
      "status": "active",
      "affected_products": 5,
      "created_at": "2025-01-01T09:30:00Z",
      "action_required": true,
      "action_url": "/inventory/low-stock"
    }
  ]
}
```

## 💰 **Cash Flow Alerts**

### **Create Cash Flow Alert**
```http
POST /api/notifications/cash-flow-alert/
```

**Description**: Create a cash flow alert

**Request Body**:
```json
{
  "solution_name": "my_business",
  "threshold_amount": 10000,
  "alert_message": "Cash balance is below minimum threshold",
  "alert_type": "low_balance",
  "severity": "high",
  "recipients": ["owner@business.com", "finance@business.com"]
}
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "alert_id": "alert_003",
    "alert_type": "cash_flow",
    "title": "Low Cash Balance Alert",
    "message": "Cash balance is below minimum threshold",
    "severity": "high",
    "status": "active",
    "threshold_amount": 10000,
    "current_balance": 5000,
    "created_at": "2025-01-01T11:00:00Z",
    "recipients": ["owner@business.com", "finance@business.com"]
  },
  "message": "Cash flow alert created successfully"
}
```

## 💳 **Payment Reminders**

### **Create Payment Reminder**
```http
POST /api/notifications/payment-reminder/
```

**Description**: Create a payment reminder

**Request Body**:
```json
{
  "solution_name": "my_business",
  "invoice_id": "INV-001",
  "customer_name": "ABC Company",
  "amount": 5000,
  "due_date": "2025-01-31T23:59:59Z",
  "reminder_type": "payment_due",
  "reminder_message": "Payment for invoice INV-001 is due on January 31st",
  "reminder_days": 7,
  "recipients": ["customer@abc.com"]
}
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "reminder_id": "reminder_001",
    "invoice_id": "INV-001",
    "customer_name": "ABC Company",
    "amount": 5000,
    "due_date": "2025-01-31T23:59:59Z",
    "reminder_type": "payment_due",
    "status": "scheduled",
    "scheduled_date": "2025-01-24T10:00:00Z",
    "recipients": ["customer@abc.com"],
    "created_at": "2025-01-01T10:00:00Z"
  },
  "message": "Payment reminder created successfully"
}
```

## 📦 **Inventory Alerts**

### **Create Inventory Alert**
```http
POST /api/notifications/inventory-alert/
```

**Description**: Create an inventory alert

**Request Body**:
```json
{
  "solution_name": "my_business",
  "product_id": "PROD-001",
  "product_name": "Product A",
  "current_stock": 5,
  "min_stock_level": 20,
  "alert_type": "low_stock",
  "severity": "medium",
  "supplier": "Supplier XYZ",
  "estimated_lead_time": 7,
  "recipients": ["inventory@business.com"]
}
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "alert_id": "alert_004",
    "product_id": "PROD-001",
    "product_name": "Product A",
    "alert_type": "low_stock",
    "title": "Low Stock Alert - Product A",
    "message": "Product A is running low on stock",
    "severity": "medium",
    "current_stock": 5,
    "min_stock_level": 20,
    "supplier": "Supplier XYZ",
    "estimated_lead_time": 7,
    "status": "active",
    "created_at": "2025-01-01T10:30:00Z",
    "recipients": ["inventory@business.com"]
  },
  "message": "Inventory alert created successfully"
}
```

## 📋 **Compliance Deadline Reminders**

### **Create Compliance Deadline Reminder**
```http
POST /api/notifications/compliance-deadline/
```

**Description**: Create a compliance deadline reminder

**Request Body**:
```json
{
  "solution_name": "my_business",
  "compliance_type": "tax_filing",
  "title": "Monthly Tax Filing Due",
  "description": "Monthly sales tax return is due",
  "deadline": "2025-01-31T23:59:59Z",
  "reminder_days": [30, 7, 1],
  "priority": "high",
  "estimated_time": "2 hours",
  "recipients": ["finance@business.com", "accountant@business.com"]
}
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "reminder_id": "reminder_002",
    "compliance_type": "tax_filing",
    "title": "Monthly Tax Filing Due",
    "description": "Monthly sales tax return is due",
    "deadline": "2025-01-31T23:59:59Z",
    "priority": "high",
    "status": "active",
    "reminder_schedule": [
      "2025-01-01T10:00:00Z",
      "2025-01-24T10:00:00Z",
      "2025-01-30T10:00:00Z"
    ],
    "recipients": ["finance@business.com", "accountant@business.com"],
    "created_at": "2025-01-01T10:00:00Z"
  },
  "message": "Compliance deadline reminder created successfully"
}
```

## 👥 **Customer Follow-up Reminders**

### **Create Customer Follow-up Reminder**
```http
POST /api/notifications/customer-followup/
```

**Description**: Create a customer follow-up reminder

**Request Body**:
```json
{
  "solution_name": "my_business",
  "customer_id": "CUST-001",
  "customer_name": "ABC Company",
  "followup_type": "post_sale",
  "title": "Customer Follow-up - ABC Company",
  "description": "Follow up on recent purchase and gather feedback",
  "scheduled_date": "2025-01-15T10:00:00Z",
  "contact_method": "email",
  "contact_person": "John Smith",
  "contact_email": "john@abc.com",
  "assigned_to": "sales@business.com",
  "priority": "medium"
}
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "reminder_id": "reminder_003",
    "customer_id": "CUST-001",
    "customer_name": "ABC Company",
    "followup_type": "post_sale",
    "title": "Customer Follow-up - ABC Company",
    "description": "Follow up on recent purchase and gather feedback",
    "scheduled_date": "2025-01-15T10:00:00Z",
    "contact_method": "email",
    "status": "scheduled",
    "assigned_to": "sales@business.com",
    "priority": "medium",
    "created_at": "2025-01-01T10:00:00Z"
  },
  "message": "Customer follow-up reminder created successfully"
}
```

## ⚙️ **Notification Settings**

### **Get Notification Settings**
```http
GET /api/notifications/settings/
```

**Description**: Get notification settings for the business

**Parameters**:
- `solution_name` (required): Business solution name

**Example Response**:
```json
{
  "success": true,
  "data": {
    "solution_name": "my_business",
    "email_notifications": {
      "enabled": true,
      "recipients": ["owner@business.com", "finance@business.com"],
      "alert_types": ["cash_flow", "inventory", "compliance"]
    },
    "sms_notifications": {
      "enabled": false,
      "recipients": [],
      "alert_types": []
    },
    "in_app_notifications": {
      "enabled": true,
      "alert_types": ["all"]
    },
    "alert_thresholds": {
      "cash_flow": {
        "low_balance": 10000,
        "critical_balance": 5000
      },
      "inventory": {
        "low_stock_percentage": 20,
        "out_of_stock": true
      }
    },
    "reminder_schedules": {
      "payment_reminders": [7, 3, 1],
      "compliance_reminders": [30, 7, 1],
      "customer_followup": 7
    }
  }
}
```

### **Update Notification Settings**
```http
POST /api/notifications/settings/update/
```

**Description**: Update notification settings

**Request Body**:
```json
{
  "solution_name": "my_business",
  "email_notifications": {
    "enabled": true,
    "recipients": ["owner@business.com", "finance@business.com", "inventory@business.com"],
    "alert_types": ["cash_flow", "inventory", "compliance", "customer"]
  },
  "sms_notifications": {
    "enabled": true,
    "recipients": ["+1234567890"],
    "alert_types": ["critical"]
  },
  "alert_thresholds": {
    "cash_flow": {
      "low_balance": 15000,
      "critical_balance": 7500
    },
    "inventory": {
      "low_stock_percentage": 25,
      "out_of_stock": true
    }
  },
  "reminder_schedules": {
    "payment_reminders": [14, 7, 3, 1],
    "compliance_reminders": [30, 14, 7, 1],
    "customer_followup": 5
  }
}
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "solution_name": "my_business",
    "settings_updated": true,
    "updated_at": "2025-01-01T12:00:00Z",
    "changes": [
      "Added SMS notifications",
      "Updated cash flow thresholds",
      "Modified reminder schedules"
    ]
  },
  "message": "Notification settings updated successfully"
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
| `409` | Conflict | Alert already exists |
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

### **Cash Flow Monitoring**
1. **Set Alerts**: Use `POST /api/notifications/cash-flow-alert/`
2. **Monitor Alerts**: Use `GET /api/notifications/alerts/`
3. **Configure Settings**: Use `POST /api/notifications/settings/update/`

### **Payment Management**
1. **Create Reminders**: Use `POST /api/notifications/payment-reminder/`
2. **Track Payments**: Use `GET /api/notifications/alerts/`

### **Inventory Management**
1. **Set Stock Alerts**: Use `POST /api/notifications/inventory-alert/`
2. **Monitor Stock**: Use `GET /api/notifications/alerts/`

### **Compliance Management**
1. **Set Deadlines**: Use `POST /api/notifications/compliance-deadline/`
2. **Track Deadlines**: Use `GET /api/notifications/alerts/`

### **Customer Engagement**
1. **Schedule Follow-ups**: Use `POST /api/notifications/customer-followup/`
2. **Track Follow-ups**: Use `GET /api/notifications/alerts/`

## 🔗 **Related Documentation**

- **[Core Operations](01_core_operations.md)** - Core API operations
- **[MSME Features](02_msme_features.md)** - MSME-specific features
- **[Workflows](05_workflows.md)** - Simplified workflows
- **[Authentication](10_authentication.md)** - Authentication details 