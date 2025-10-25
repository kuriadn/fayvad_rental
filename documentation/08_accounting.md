# Simple Accounting API 💰

**Copyright © 2025 Fayvad Digital. All rights reserved.**

## 🎯 **Overview**

Simple accounting provides MSME-specific accounting capabilities including cash basis accounting, basic general ledger, income/expense tracking, simple financial reports, and basic tax calculations.

## 🔐 **Authentication**

All endpoints require **Handshake Authentication**:
```bash
Authorization: Bearer <handshake_token>
```

## 💵 **Cash Basis Accounting**

### **Create Cash Basis Entry**
```http
POST /api/accounting/cash-basis-entry/
```

**Description**: Create a cash basis accounting entry

**Request Body**:
```json
{
  "solution_name": "my_business",
  "entry_type": "income",
  "description": "Payment received from ABC Company",
  "amount": 5000,
  "category": "sales",
  "date": "2025-01-01",
  "reference": "INV-001",
  "payment_method": "bank_transfer",
  "notes": "Payment for invoice INV-001"
}
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "entry_id": "entry_001",
    "entry_type": "income",
    "description": "Payment received from ABC Company",
    "amount": 5000,
    "category": "sales",
    "date": "2025-01-01",
    "reference": "INV-001",
    "payment_method": "bank_transfer",
    "balance_after": 25000,
    "created_at": "2025-01-01T10:00:00Z"
  },
  "message": "Cash basis entry created successfully"
}
```

### **Get Basic Ledger**
```http
GET /api/accounting/basic-ledger/
```

**Description**: Get basic general ledger

**Parameters**:
- `solution_name` (required): Business solution name
- `date_from` (optional): Start date
- `date_to` (optional): End date
- `entry_type` (optional): Filter by entry type (income, expense)
- `category` (optional): Filter by category
- `limit` (optional): Number of records (default: 100)

**Example Response**:
```json
{
  "success": true,
  "data": {
    "period": {
      "from": "2025-01-01",
      "to": "2025-01-31"
    },
    "summary": {
      "total_income": 125000,
      "total_expenses": 95000,
      "net_income": 30000,
      "opening_balance": 20000,
      "closing_balance": 50000
    },
    "entries": [
      {
        "entry_id": "entry_001",
        "date": "2025-01-01",
        "entry_type": "income",
        "description": "Payment received from ABC Company",
        "amount": 5000,
        "category": "sales",
        "reference": "INV-001",
        "balance": 25000
      },
      {
        "entry_id": "entry_002",
        "date": "2025-01-02",
        "entry_type": "expense",
        "description": "Office supplies purchase",
        "amount": 500,
        "category": "office_expenses",
        "reference": "PO-001",
        "balance": 24500
      }
    ]
  }
}
```

## 📊 **Income/Expense Tracking**

### **Track Income/Expense**
```http
POST /api/accounting/income-expense/
```

**Description**: Track income or expense

**Request Body**:
```json
{
  "solution_name": "my_business",
  "type": "expense",
  "description": "Rent payment for January",
  "amount": 3000,
  "category": "rent",
  "date": "2025-01-01",
  "payment_method": "bank_transfer",
  "vendor": "Property Management Co",
  "reference": "RENT-001",
  "notes": "Monthly rent payment"
}
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "tracking_id": "track_001",
    "type": "expense",
    "description": "Rent payment for January",
    "amount": 3000,
    "category": "rent",
    "date": "2025-01-01",
    "payment_method": "bank_transfer",
    "vendor": "Property Management Co",
    "reference": "RENT-001",
    "created_at": "2025-01-01T10:00:00Z"
  },
  "message": "Income/expense tracked successfully"
}
```

### **Get Income/Expense Summary**
```http
GET /api/accounting/income-expense-summary/
```

**Description**: Get income/expense summary

**Parameters**:
- `solution_name` (required): Business solution name
- `period` (optional): Time period (month, quarter, year)
- `date_from` (optional): Start date
- `date_to` (optional): End date

**Example Response**:
```json
{
  "success": true,
  "data": {
    "period": "month",
    "date_range": {
      "from": "2025-01-01",
      "to": "2025-01-31"
    },
    "summary": {
      "total_income": 125000,
      "total_expenses": 95000,
      "net_income": 30000,
      "profit_margin": 24.0
    },
    "income_by_category": [
      {
        "category": "sales",
        "amount": 120000,
        "percentage": 96.0
      },
      {
        "category": "services",
        "amount": 5000,
        "percentage": 4.0
      }
    ],
    "expenses_by_category": [
      {
        "category": "rent",
        "amount": 3000,
        "percentage": 3.2
      },
      {
        "category": "utilities",
        "amount": 800,
        "percentage": 0.8
      },
      {
        "category": "payroll",
        "amount": 45000,
        "percentage": 47.4
      }
    ]
  }
}
```

## 📈 **Financial Reports**

### **Generate Basic Report**
```http
POST /api/accounting/basic-report/
```

**Description**: Generate a basic financial report

**Request Body**:
```json
{
  "solution_name": "my_business",
  "report_type": "profit_loss",
  "period": "monthly",
  "date_from": "2025-01-01",
  "date_to": "2025-01-31",
  "format": "pdf",
  "include_details": true,
  "comparison_period": "previous_month"
}
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "report_id": "report_001",
    "report_type": "profit_loss",
    "period": "monthly",
    "date_range": {
      "from": "2025-01-01",
      "to": "2025-01-31"
    },
    "status": "generated",
    "generated_at": "2025-01-01T10:00:00Z",
    "summary": {
      "revenue": 125000,
      "expenses": 95000,
      "net_income": 30000,
      "profit_margin": 24.0,
      "growth": 15.5
    },
    "download_url": "https://api.fayvad.com/api/accounting/reports/download/report_001"
  },
  "message": "Basic report generated successfully"
}
```

### **Calculate Basic Tax**
```http
POST /api/accounting/basic-tax/
```

**Description**: Calculate basic tax

**Request Body**:
```json
{
  "solution_name": "my_business",
  "tax_year": 2025,
  "business_type": "llc",
  "net_income": 30000,
  "deductions": {
    "business_expenses": 95000,
    "depreciation": 5000,
    "home_office": 2000
  },
    "tax_rates": {
    "federal": 15.0,
    "state": 5.0,
    "self_employment": 15.3
  }
}
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "tax_calculation_id": "tax_001",
    "tax_year": 2025,
    "business_type": "llc",
    "gross_income": 125000,
    "total_deductions": 102000,
    "net_income": 23000,
    "tax_breakdown": {
      "federal_tax": 3450,
      "state_tax": 1150,
      "self_employment_tax": 3519,
      "total_tax": 8119
    },
    "effective_tax_rate": 35.3,
    "estimated_quarterly_payments": 2030,
    "calculation_date": "2025-01-01T10:00:00Z"
  },
  "message": "Tax calculation completed successfully"
}
```

## 💰 **Cash Position**

### **Get Cash Position**
```http
GET /api/accounting/cash-position/
```

**Description**: Get current cash position

**Parameters**:
- `solution_name` (required): Business solution name
- `date` (optional): Specific date (default: today)

**Example Response**:
```json
{
  "success": true,
  "data": {
    "date": "2025-01-01",
    "cash_position": {
      "opening_balance": 20000,
      "total_inflows": 125000,
      "total_outflows": 95000,
      "closing_balance": 50000,
      "net_change": 30000
    },
    "cash_flow": {
      "operating": 35000,
      "investing": -5000,
      "financing": 0,
      "net_cash_flow": 30000
    },
    "projections": {
      "next_week": 52000,
      "next_month": 60000,
      "next_quarter": 75000
    },
    "alerts": [
      {
        "type": "low_balance",
        "message": "Cash balance approaching minimum threshold",
        "severity": "medium"
      }
    ]
  }
}
```

### **Get Accounting Summary**
```http
GET /api/accounting/summary/
```

**Description**: Get comprehensive accounting summary

**Parameters**:
- `solution_name` (required): Business solution name
- `period` (optional): Time period (month, quarter, year)

**Example Response**:
```json
{
  "success": true,
  "data": {
    "period": "month",
    "financial_summary": {
      "total_revenue": 125000,
      "total_expenses": 95000,
      "net_income": 30000,
      "profit_margin": 24.0,
      "cash_balance": 50000,
      "accounts_receivable": 15000,
      "accounts_payable": 8000
    },
    "key_metrics": {
      "revenue_growth": 15.5,
      "expense_ratio": 76.0,
      "cash_flow_ratio": 1.2,
      "debt_to_equity": 0.3
    },
    "top_categories": {
      "income": [
        {"category": "sales", "amount": 120000, "percentage": 96.0}
      ],
      "expenses": [
        {"category": "payroll", "amount": 45000, "percentage": 47.4},
        {"category": "rent", "amount": 3000, "percentage": 3.2}
      ]
    },
    "trends": {
      "revenue_trend": "increasing",
      "expense_trend": "stable",
      "profit_trend": "increasing",
      "cash_trend": "increasing"
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
| `409` | Conflict | Entry already exists |
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

### **Daily Accounting**
1. **Record Transactions**: Use `POST /api/accounting/cash-basis-entry/`
2. **Track Income/Expense**: Use `POST /api/accounting/income-expense/`
3. **View Ledger**: Use `GET /api/accounting/basic-ledger/`

### **Financial Reporting**
1. **Generate Reports**: Use `POST /api/accounting/basic-report/`
2. **Calculate Tax**: Use `POST /api/accounting/basic-tax/`
3. **Get Summary**: Use `GET /api/accounting/summary/`

### **Cash Management**
1. **Monitor Cash**: Use `GET /api/accounting/cash-position/`
2. **Track Flow**: Use `GET /api/accounting/income-expense-summary/`

## 🔗 **Related Documentation**

- **[Core Operations](01_core_operations.md)** - Core API operations
- **[MSME Features](02_msme_features.md)** - MSME-specific features
- **[Compliance](07_compliance.md)** - Compliance management
- **[Authentication](10_authentication.md)** - Authentication details 