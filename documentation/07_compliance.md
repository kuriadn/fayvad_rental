# Compliance Management API 📋

**Copyright © 2025 Fayvad Digital. All rights reserved.**

## 🎯 **Overview**

Compliance management provides MSME-specific compliance tools including tax calculations, basic payroll processing, audit trails, compliance deadline tracking, and regulatory reporting.

## 🔐 **Authentication**

All endpoints require **Handshake Authentication**:
```bash
Authorization: Bearer <handshake_token>
```

## 💰 **Tax Calculations**

### **Calculate Tax**
```http
POST /api/compliance/calculate-tax/
```

**Description**: Calculate tax for transactions

**Request Body**:
```json
{
  "solution_name": "my_business",
  "transaction_type": "sale",
  "amount": 1000,
  "tax_type": "sales_tax",
  "location": "CA",
  "tax_rates": {
    "state_tax": 7.25,
    "local_tax": 1.0,
    "special_tax": 0.5
  },
  "exemptions": ["resale", "non_profit"],
  "date": "2025-01-01"
}
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "transaction_id": "txn_001",
    "transaction_type": "sale",
    "amount": 1000,
    "tax_breakdown": {
      "state_tax": 72.50,
      "local_tax": 10.00,
      "special_tax": 5.00,
      "total_tax": 87.50
    },
    "tax_rate": 8.75,
    "total_amount": 1087.50,
    "exemptions_applied": ["resale"],
    "calculation_date": "2025-01-01T10:00:00Z"
  },
  "message": "Tax calculation completed successfully"
}
```

## 👥 **Payroll Basics**

### **Process Payroll Basics**
```http
POST /api/compliance/payroll-basics/
```

**Description**: Process basic payroll calculations

**Request Body**:
```json
{
  "solution_name": "my_business",
  "employee_id": "EMP-001",
  "employee_name": "John Smith",
  "pay_period": "monthly",
  "gross_pay": 5000,
  "hours_worked": 160,
  "overtime_hours": 10,
  "deductions": {
    "federal_tax": 800,
    "state_tax": 200,
    "social_security": 310,
    "medicare": 72.50,
    "health_insurance": 200
  },
  "benefits": {
    "health_insurance": 200,
    "retirement": 250
  }
}
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "payroll_id": "payroll_001",
    "employee_id": "EMP-001",
    "employee_name": "John Smith",
    "pay_period": "monthly",
    "gross_pay": 5000,
    "total_deductions": 1582.50,
    "net_pay": 3417.50,
    "tax_breakdown": {
      "federal_tax": 800,
      "state_tax": 200,
      "social_security": 310,
      "medicare": 72.50
    },
    "benefits": {
      "health_insurance": 200,
      "retirement": 250
    },
    "processed_at": "2025-01-01T10:00:00Z"
  },
  "message": "Payroll processed successfully"
}
```

## 📝 **Audit Trails**

### **Create Audit Trail**
```http
POST /api/compliance/audit-trail/
```

**Description**: Create an audit trail entry

**Request Body**:
```json
{
  "solution_name": "my_business",
  "action": "create_invoice",
  "user": "john.doe",
  "resource_type": "invoice",
  "resource_id": "INV-001",
  "details": {
    "customer": "ABC Company",
    "amount": 5000,
    "items": ["Product A", "Product B"]
  },
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "timestamp": "2025-01-01T10:00:00Z"
}
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "audit_id": "audit_001",
    "action": "create_invoice",
    "user": "john.doe",
    "resource_type": "invoice",
    "resource_id": "INV-001",
    "status": "success",
    "timestamp": "2025-01-01T10:00:00Z",
    "ip_address": "192.168.1.100",
    "session_id": "session_123"
  },
  "message": "Audit trail entry created successfully"
}
```

### **Get Audit Trail**
```http
GET /api/compliance/audit-trail/get/
```

**Description**: Get audit trail entries

**Parameters**:
- `solution_name` (required): Business solution name
- `action` (optional): Filter by action type
- `user` (optional): Filter by user
- `resource_type` (optional): Filter by resource type
- `date_from` (optional): Start date
- `date_to` (optional): End date
- `limit` (optional): Number of records (default: 100)

**Example Response**:
```json
{
  "success": true,
  "data": [
    {
      "audit_id": "audit_001",
      "action": "create_invoice",
      "user": "john.doe",
      "resource_type": "invoice",
      "resource_id": "INV-001",
      "details": {
        "customer": "ABC Company",
        "amount": 5000
      },
      "status": "success",
      "timestamp": "2025-01-01T10:00:00Z",
      "ip_address": "192.168.1.100"
    },
    {
      "audit_id": "audit_002",
      "action": "update_customer",
      "user": "jane.smith",
      "resource_type": "customer",
      "resource_id": "CUST-001",
      "details": {
        "field": "email",
        "old_value": "old@email.com",
        "new_value": "new@email.com"
      },
      "status": "success",
      "timestamp": "2025-01-01T09:30:00Z",
      "ip_address": "192.168.1.101"
    }
  ]
}
```

## 📅 **Compliance Deadlines**

### **Create Compliance Deadline**
```http
POST /api/compliance/deadline/
```

**Description**: Create a compliance deadline

**Request Body**:
```json
{
  "solution_name": "my_business",
  "compliance_type": "tax_filing",
  "title": "Monthly Sales Tax Return",
  "description": "File monthly sales tax return for January 2025",
  "deadline": "2025-02-15T23:59:59Z",
  "priority": "high",
  "estimated_time": "2 hours",
  "responsible_person": "finance@business.com",
  "reminder_days": [30, 7, 1],
  "penalty_amount": 500,
  "penalty_description": "Late filing penalty"
}
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "deadline_id": "deadline_001",
    "compliance_type": "tax_filing",
    "title": "Monthly Sales Tax Return",
    "description": "File monthly sales tax return for January 2025",
    "deadline": "2025-02-15T23:59:59Z",
    "priority": "high",
    "status": "pending",
    "responsible_person": "finance@business.com",
    "reminder_schedule": [
      "2025-01-16T10:00:00Z",
      "2025-02-08T10:00:00Z",
      "2025-02-14T10:00:00Z"
    ],
    "created_at": "2025-01-01T10:00:00Z"
  },
  "message": "Compliance deadline created successfully"
}
```

### **Get Compliance Deadlines**
```http
GET /api/compliance/deadlines/
```

**Description**: Get compliance deadlines

**Parameters**:
- `solution_name` (required): Business solution name
- `compliance_type` (optional): Filter by compliance type
- `status` (optional): Filter by status (pending, completed, overdue)
- `priority` (optional): Filter by priority (low, medium, high, critical)

**Example Response**:
```json
{
  "success": true,
  "data": [
    {
      "deadline_id": "deadline_001",
      "compliance_type": "tax_filing",
      "title": "Monthly Sales Tax Return",
      "description": "File monthly sales tax return for January 2025",
      "deadline": "2025-02-15T23:59:59Z",
      "priority": "high",
      "status": "pending",
      "days_remaining": 45,
      "responsible_person": "finance@business.com",
      "penalty_amount": 500
    },
    {
      "deadline_id": "deadline_002",
      "compliance_type": "business_license",
      "title": "Business License Renewal",
      "description": "Renew business operating license",
      "deadline": "2025-03-31T23:59:59Z",
      "priority": "medium",
      "status": "pending",
      "days_remaining": 89,
      "responsible_person": "admin@business.com",
      "penalty_amount": 1000
    }
  ]
}
```

## 📊 **Regulatory Reports**

### **Generate Regulatory Report**
```http
POST /api/compliance/regulatory-report/
```

**Description**: Generate a regulatory report

**Request Body**:
```json
{
  "solution_name": "my_business",
  "report_type": "sales_tax_summary",
  "period": "monthly",
  "date_from": "2025-01-01",
  "date_to": "2025-01-31",
  "format": "pdf",
  "include_details": true,
  "filing_requirements": {
    "state": "CA",
    "local_jurisdiction": "Los Angeles",
    "filing_frequency": "monthly"
  }
}
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "report_id": "report_001",
    "report_type": "sales_tax_summary",
    "period": "monthly",
    "date_range": {
      "from": "2025-01-01",
      "to": "2025-01-31"
    },
    "status": "generated",
    "generated_at": "2025-01-01T10:00:00Z",
    "summary": {
      "total_sales": 125000,
      "taxable_sales": 120000,
      "total_tax_collected": 10500,
      "state_tax": 8700,
      "local_tax": 1200,
      "special_tax": 600
    },
    "download_url": "https://api.fayvad.com/api/compliance/reports/download/report_001",
    "filing_deadline": "2025-02-15T23:59:59Z"
  },
  "message": "Regulatory report generated successfully"
}
```

### **Get Compliance Summary**
```http
GET /api/compliance/summary/
```

**Description**: Get compliance summary for the business

**Parameters**:
- `solution_name` (required): Business solution name
- `period` (optional): Time period (month, quarter, year)

**Example Response**:
```json
{
  "success": true,
  "data": {
    "period": "month",
    "compliance_overview": {
      "total_deadlines": 5,
      "completed": 3,
      "pending": 2,
      "overdue": 0,
      "compliance_rate": 60.0
    },
    "tax_compliance": {
      "sales_tax_filed": true,
      "payroll_tax_filed": true,
      "income_tax_filed": false,
      "next_deadline": "2025-02-15T23:59:59Z"
    },
    "regulatory_filings": {
      "business_license": "active",
      "permits": "up_to_date",
      "insurance": "active",
      "next_renewal": "2025-03-31T23:59:59Z"
    },
    "audit_status": {
      "last_audit": "2024-12-01T00:00:00Z",
      "audit_score": 95,
      "findings": 2,
      "resolved": 2
    },
    "risk_assessment": {
      "overall_risk": "low",
      "high_risk_areas": [],
      "recommendations": [
        "File income tax return by deadline",
        "Review payroll calculations monthly"
      ]
    }
  }
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
| `409` | Conflict | Deadline already exists |
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

### **Tax Management**
1. **Calculate Tax**: Use `POST /api/compliance/calculate-tax/`
2. **Generate Reports**: Use `POST /api/compliance/regulatory-report/`
3. **Track Deadlines**: Use `GET /api/compliance/deadlines/`

### **Payroll Processing**
1. **Process Payroll**: Use `POST /api/compliance/payroll-basics/`
2. **Track Compliance**: Use `GET /api/compliance/summary/`

### **Audit Management**
1. **Create Audit Trail**: Use `POST /api/compliance/audit-trail/`
2. **Review Audit Log**: Use `GET /api/compliance/audit-trail/get/`

### **Compliance Tracking**
1. **Set Deadlines**: Use `POST /api/compliance/deadline/`
2. **Monitor Deadlines**: Use `GET /api/compliance/deadlines/`
3. **Get Summary**: Use `GET /api/compliance/summary/`

## 🔗 **Related Documentation**

- **[Core Operations](01_core_operations.md)** - Core API operations
- **[MSME Features](02_msme_features.md)** - MSME-specific features
- **[Notifications](06_notifications.md)** - Notification system
- **[Authentication](10_authentication.md)** - Authentication details 