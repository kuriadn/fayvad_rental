# Analytics & Dashboards API 📊

**Copyright © 2025 Fayvad Digital. All rights reserved.**

## 🎯 **Overview**

Analytics and dashboards provide comprehensive business intelligence for MSMEs including business overview, daily cash position, sales summary, customer activity, profit tracking, and performance metrics.

## 🔐 **Authentication**

All endpoints require **Handshake Authentication**:
```bash
Authorization: Bearer <handshake_token>
```

## 📈 **Business Overview**

### **Get Business Overview**
```http
GET /api/analytics/business-overview/
```

**Description**: Get comprehensive business overview

**Parameters**:
- `solution_name` (required): Business solution name
- `period` (optional): Time period (day, week, month, quarter, year)

**Example Response**:
```json
{
  "success": true,
  "data": {
    "period": "month",
    "business_summary": {
      "total_revenue": 125000,
      "total_expenses": 95000,
      "net_profit": 30000,
      "profit_margin": 24.0,
      "cash_balance": 50000
    },
    "key_metrics": {
      "total_customers": 45,
      "total_orders": 147,
      "average_order_value": 850,
      "customer_satisfaction": 4.2
    },
    "growth_indicators": {
      "revenue_growth": 15.5,
      "customer_growth": 12.5,
      "profit_growth": 18.2
    },
    "trends": {
      "revenue_trend": "increasing",
      "profit_trend": "increasing",
      "customer_trend": "stable"
    }
  }
}
```

## 💰 **Daily Cash Position**

### **Get Daily Cash Position**
```http
GET /api/analytics/daily-cash-position/
```

**Description**: Get daily cash position and flow

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
      "closing_balance": 25000,
      "net_change": 5000,
      "total_inflows": 8000,
      "total_outflows": 3000
    },
    "cash_flow_breakdown": {
      "sales_receipts": 7500,
      "other_income": 500,
      "operating_expenses": 2500,
      "payroll": 500
    },
    "projections": {
      "next_day": 26000,
      "next_week": 30000,
      "next_month": 45000
    }
  }
}
```

## 📊 **Sales Summary**

### **Get Sales Summary**
```http
GET /api/analytics/sales-summary/
```

**Description**: Get detailed sales summary

**Parameters**:
- `solution_name` (required): Business solution name
- `period` (optional): Time period
- `date_from` (optional): Start date
- `date_to` (optional): End date

**Example Response**:
```json
{
  "success": true,
  "data": {
    "period": "month",
    "sales_summary": {
      "total_sales": 125000,
      "total_orders": 147,
      "average_order_value": 850,
      "sales_growth": 15.5
    },
    "sales_by_category": [
      {
        "category": "Electronics",
        "sales": 45000,
        "percentage": 36.0,
        "units_sold": 45
      },
      {
        "category": "Clothing",
        "sales": 38000,
        "percentage": 30.4,
        "units_sold": 95
      }
    ],
    "top_products": [
      {
        "product": "Product A",
        "sales": 15000,
        "units_sold": 120
      },
      {
        "product": "Product B",
        "sales": 12000,
        "units_sold": 95
      }
    ]
  }
}
```

## 👥 **Customer Activity**

### **Get Customer Activity**
```http
GET /api/analytics/customer-activity/
```

**Description**: Get customer activity analytics

**Parameters**:
- `solution_name` (required): Business solution name
- `period` (optional): Time period

**Example Response**:
```json
{
  "success": true,
  "data": {
    "period": "month",
    "customer_summary": {
      "total_customers": 45,
      "new_customers": 8,
      "repeat_customers": 37,
      "customer_satisfaction": 4.2
    },
    "customer_segments": [
      {
        "segment": "High Value",
        "count": 10,
        "total_spent": 45000,
        "average_spent": 4500
      },
      {
        "segment": "Regular",
        "count": 25,
        "total_spent": 60000,
        "average_spent": 2400
      }
    ],
    "top_customers": [
      {
        "customer": "ABC Company",
        "total_spent": 8500,
        "orders": 12,
        "last_order": "2025-01-01"
      }
    ]
  }
}
```

## 📈 **Profit Tracking**

### **Get Profit Tracking**
```http
GET /api/analytics/profit-tracking/
```

**Description**: Get profit tracking analytics

**Parameters**:
- `solution_name` (required): Business solution name
- `period` (optional): Time period

**Example Response**:
```json
{
  "success": true,
  "data": {
    "period": "month",
    "profit_summary": {
      "total_revenue": 125000,
      "total_expenses": 95000,
      "net_profit": 30000,
      "profit_margin": 24.0,
      "profit_growth": 18.2
    },
    "profit_by_category": [
      {
        "category": "Electronics",
        "revenue": 45000,
        "expenses": 32000,
        "profit": 13000,
        "margin": 28.9
      },
      {
        "category": "Clothing",
        "revenue": 38000,
        "expenses": 28000,
        "profit": 10000,
        "margin": 26.3
      }
    ],
    "profit_trends": {
      "daily": [1200, 1350, 1100, 1400],
      "weekly": [8500, 9200, 7800, 9500],
      "monthly": [28000, 30000, 32000, 30000]
    }
  }
}
```

## 📦 **Inventory Analytics**

### **Get Inventory Analytics**
```http
GET /api/analytics/inventory-analytics/
```

**Description**: Get inventory analytics

**Parameters**:
- `solution_name` (required): Business solution name

**Example Response**:
```json
{
  "success": true,
  "data": {
    "inventory_summary": {
      "total_products": 150,
      "total_value": 45000,
      "low_stock_items": 5,
      "out_of_stock_items": 2
    },
    "inventory_by_category": [
      {
        "category": "Electronics",
        "products": 45,
        "value": 18000,
        "turnover_rate": 4.2
      },
      {
        "category": "Clothing",
        "products": 60,
        "value": 15000,
        "turnover_rate": 3.8
      }
    ],
    "top_selling_products": [
      {
        "product": "Product A",
        "units_sold": 120,
        "revenue": 15000,
        "stock_level": 25
      }
    ],
    "low_stock_alerts": [
      {
        "product": "Product B",
        "current_stock": 5,
        "min_stock": 20,
        "days_remaining": 3
      }
    ]
  }
}
```

## 📊 **Performance Metrics**

### **Get Performance Metrics**
```http
GET /api/analytics/performance-metrics/
```

**Description**: Get comprehensive performance metrics

**Parameters**:
- `solution_name` (required): Business solution name
- `period` (optional): Time period

**Example Response**:
```json
{
  "success": true,
  "data": {
    "period": "month",
    "financial_metrics": {
      "revenue_growth": 15.5,
      "profit_margin": 24.0,
      "cash_flow_ratio": 1.2,
      "debt_to_equity": 0.3
    },
    "operational_metrics": {
      "order_fulfillment_rate": 98.5,
      "average_order_processing_time": "2.5 hours",
      "customer_satisfaction": 4.2,
      "employee_productivity": 85.0
    },
    "customer_metrics": {
      "customer_acquisition_cost": 150,
      "customer_lifetime_value": 2500,
      "customer_retention_rate": 82.0,
      "net_promoter_score": 8.5
    },
    "inventory_metrics": {
      "inventory_turnover": 4.2,
      "stockout_rate": 1.3,
      "carrying_cost": 8.5,
      "order_accuracy": 99.2
    }
  }
}
```

## 📊 **MSME Dashboard**

### **Get MSME Dashboard**
```http
GET /api/analytics/msme-dashboard/
```

**Description**: Get comprehensive MSME dashboard

**Parameters**:
- `solution_name` (required): Business solution name
- `dashboard_type` (optional): Dashboard type (overview, financial, operational)

**Example Response**:
```json
{
  "success": true,
  "data": {
    "dashboard_type": "overview",
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
    ],
    "quick_actions": [
      {
        "action": "create_invoice",
        "label": "Create Invoice",
        "url": "/invoices/create"
      },
      {
        "action": "add_customer",
        "label": "Add Customer",
        "url": "/customers/create"
      }
    ]
  }
}
```

## 📈 **Custom Reports**

### **Generate Custom Report**
```http
POST /api/analytics/custom-report/
```

**Description**: Generate a custom analytics report

**Request Body**:
```json
{
  "solution_name": "my_business",
  "report_type": "sales_analysis",
  "parameters": {
    "date_from": "2025-01-01",
    "date_to": "2025-01-31",
    "categories": ["electronics", "clothing"],
    "metrics": ["revenue", "profit", "units_sold"]
  },
  "format": "pdf",
  "include_charts": true
}
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "report_id": "custom_report_001",
    "report_type": "sales_analysis",
    "parameters": {
      "date_from": "2025-01-01",
      "date_to": "2025-01-31"
    },
    "status": "generated",
    "generated_at": "2025-01-01T10:00:00Z",
    "download_url": "https://api.fayvad.com/api/analytics/reports/download/custom_report_001"
  },
  "message": "Custom report generated successfully"
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

### **Business Monitoring**
1. **Get Overview**: Use `GET /api/analytics/business-overview/`
2. **Monitor Cash**: Use `GET /api/analytics/daily-cash-position/`
3. **Track Performance**: Use `GET /api/analytics/performance-metrics/`

### **Sales Analysis**
1. **Sales Summary**: Use `GET /api/analytics/sales-summary/`
2. **Profit Tracking**: Use `GET /api/analytics/profit-tracking/`
3. **Customer Activity**: Use `GET /api/analytics/customer-activity/`

### **Inventory Management**
1. **Inventory Analytics**: Use `GET /api/analytics/inventory-analytics/`
2. **Dashboard View**: Use `GET /api/analytics/msme-dashboard/`

### **Custom Reporting**
1. **Generate Reports**: Use `POST /api/analytics/custom-report/`

## 🔗 **Related Documentation**

- **[Core Operations](01_core_operations.md)** - Core API operations
- **[MSME Features](02_msme_features.md)** - MSME-specific features
- **[Business Intelligence](04_business_intelligence.md)** - BI and analytics
- **[Authentication](10_authentication.md)** - Authentication details 