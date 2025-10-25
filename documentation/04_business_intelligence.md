# Business Intelligence API 📊

**Copyright © 2025 Fayvad Digital. All rights reserved.**

## 🎯 **Overview**

Business Intelligence (BI) features provide comprehensive analytics, reporting, and dashboard capabilities for business performance monitoring and decision-making.

## 🔐 **Authentication**

All endpoints require **Handshake Authentication**:
```bash
Authorization: Bearer <handshake_token>
```

## 📈 **Analytics Data**

### **Get Analytics Data**
```http
GET /api/bi/analytics/
```

**Description**: Get comprehensive analytics data

**Parameters**:
- `solution_name` (required): Business solution name
- `period` (optional): Time period (day, week, month, quarter, year)
- `date_from` (optional): Start date (YYYY-MM-DD)
- `date_to` (optional): End date (YYYY-MM-DD)
- `metrics` (optional): Comma-separated metrics list

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
    "sales_analytics": {
      "total_sales": 125000,
      "sales_growth": 15.5,
      "average_order_value": 850,
      "sales_by_day": [
        {"date": "2025-01-01", "sales": 4200},
        {"date": "2025-01-02", "sales": 3800}
      ]
    },
    "customer_analytics": {
      "total_customers": 45,
      "new_customers": 8,
      "repeat_customers": 37,
      "customer_satisfaction": 4.2,
      "top_customers": [
        {"name": "Customer A", "total_spent": 8500},
        {"name": "Customer B", "total_spent": 7200}
      ]
    },
    "product_analytics": {
      "total_products": 150,
      "top_selling_products": [
        {"name": "Product A", "units_sold": 120, "revenue": 15000},
        {"name": "Product B", "units_sold": 95, "revenue": 12000}
      ],
      "low_stock_products": 5
    },
    "financial_analytics": {
      "total_revenue": 125000,
      "total_expenses": 95000,
      "net_profit": 30000,
      "profit_margin": 24.0,
      "cash_flow": 25000
    }
  }
}
```

## 📊 **Reports**

### **Sales Report**
```http
GET /api/bi/reports/sales/
```

**Description**: Get detailed sales report

**Parameters**:
- `solution_name` (required): Business solution name
- `report_type` (optional): Report type (summary, detailed, by_product, by_customer)
- `period` (optional): Time period
- `date_from` (optional): Start date
- `date_to` (optional): End date
- `format` (optional): Output format (json, csv, pdf)

**Example Response**:
```json
{
  "success": true,
  "data": {
    "report_type": "summary",
    "period": "month",
    "date_range": {
      "from": "2025-01-01",
      "to": "2025-01-31"
    },
    "summary": {
      "total_sales": 125000,
      "total_orders": 147,
      "average_order_value": 850,
      "sales_growth": 15.5,
      "top_sales_day": "2025-01-15"
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
    "sales_by_customer": [
      {
        "customer": "Customer A",
        "total_spent": 8500,
        "orders": 12,
        "average_order": 708
      }
    ]
  }
}
```

### **Inventory Report**
```http
GET /api/bi/reports/inventory/
```

**Description**: Get detailed inventory report

**Parameters**:
- `solution_name` (required): Business solution name
- `report_type` (optional): Report type (summary, low_stock, movements, valuation)
- `category` (optional): Filter by product category

**Example Response**:
```json
{
  "success": true,
  "data": {
    "report_type": "summary",
    "summary": {
      "total_products": 150,
      "total_value": 45000,
      "low_stock_items": 5,
      "out_of_stock_items": 2,
      "average_stock_level": 25
    },
    "inventory_by_category": [
      {
        "category": "Electronics",
        "products": 45,
        "total_value": 18000,
        "average_stock": 30
      },
      {
        "category": "Clothing",
        "products": 60,
        "total_value": 15000,
        "average_stock": 20
      }
    ],
    "low_stock_alerts": [
      {
        "product": "Product A",
        "current_stock": 5,
        "min_stock": 10,
        "category": "Electronics"
      }
    ]
  }
}
```

### **Available Reports**
```http
GET /api/bi/reports/
```

**Description**: Get list of available reports

**Example Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": "sales_summary",
      "name": "Sales Summary Report",
      "description": "Overview of sales performance",
      "categories": ["sales", "performance"],
      "parameters": ["period", "date_from", "date_to"],
      "formats": ["json", "csv", "pdf"]
    },
    {
      "id": "inventory_valuation",
      "name": "Inventory Valuation Report",
      "description": "Current inventory value and status",
      "categories": ["inventory", "finance"],
      "parameters": ["category", "valuation_method"],
      "formats": ["json", "csv", "pdf"]
    },
    {
      "id": "customer_analysis",
      "name": "Customer Analysis Report",
      "description": "Customer behavior and performance",
      "categories": ["customers", "analytics"],
      "parameters": ["period", "customer_segment"],
      "formats": ["json", "csv", "pdf"]
    }
  ]
}
```

### **Execute Report**
```http
POST /api/bi/reports/execute/
```

**Description**: Execute a specific report

**Request Body**:
```json
{
  "solution_name": "my_business",
  "report_id": "sales_summary",
  "parameters": {
    "period": "month",
    "date_from": "2025-01-01",
    "date_to": "2025-01-31"
  },
  "format": "json"
}
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "report_id": "sales_summary",
    "execution_id": "exec_123",
    "status": "completed",
    "generated_at": "2025-01-01T12:00:00Z",
    "download_url": "https://api.fayvad.com/api/bi/reports/download/exec_123"
  }
}
```

## 📊 **Dashboards**

### **Get Dashboard Data**
```http
GET /api/bi/dashboards/{dashboard_type}/
```

**Description**: Get dashboard data by type

**Parameters**:
- `dashboard_type` (required): Dashboard type (overview, sales, inventory, customers, finance)
- `solution_name` (required): Business solution name
- `period` (optional): Time period

**Example Response**:
```json
{
  "success": true,
  "data": {
    "dashboard_type": "overview",
    "period": "month",
    "widgets": {
      "sales_summary": {
        "title": "Sales Summary",
        "type": "metric",
        "data": {
          "total_sales": 125000,
          "growth": 15.5,
          "trend": "up"
        }
      },
      "recent_orders": {
        "title": "Recent Orders",
        "type": "list",
        "data": [
          {
            "order_id": "ORD-001",
            "customer": "Customer A",
            "amount": 1200,
            "status": "completed",
            "date": "2025-01-01T10:30:00Z"
          }
        ]
      },
      "top_products": {
        "title": "Top Products",
        "type": "chart",
        "data": [
          {"name": "Product A", "sales": 15000},
          {"name": "Product B", "sales": 12000}
        ]
      }
    }
  }
}
```

### **Available Dashboards**
```http
GET /api/bi/dashboards/
```

**Description**: Get list of available dashboards

**Example Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": "overview",
      "name": "Business Overview",
      "description": "High-level business metrics and KPIs",
      "widgets": ["sales_summary", "recent_orders", "top_products"],
      "refresh_interval": 300
    },
    {
      "id": "sales",
      "name": "Sales Dashboard",
      "description": "Detailed sales performance and trends",
      "widgets": ["sales_chart", "sales_by_category", "sales_by_customer"],
      "refresh_interval": 300
    },
    {
      "id": "inventory",
      "name": "Inventory Dashboard",
      "description": "Inventory levels and stock management",
      "widgets": ["stock_levels", "low_stock_alerts", "inventory_movements"],
      "refresh_interval": 600
    }
  ]
}
```

### **Dashboard Widgets**
```http
GET /api/bi/dashboards/{dashboard_id}/widgets/
```

**Description**: Get widgets for a specific dashboard

**Example Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": "sales_summary",
      "name": "Sales Summary",
      "type": "metric",
      "description": "Key sales metrics",
      "config": {
        "metrics": ["total_sales", "growth", "orders"],
        "period": "month"
      }
    },
    {
      "id": "recent_orders",
      "name": "Recent Orders",
      "type": "list",
      "description": "Latest orders",
      "config": {
        "limit": 10,
        "sort_by": "date",
        "sort_order": "desc"
      }
    }
  ]
}
```

## 📊 **KPI Summary**

### **Get KPI Summary**
```http
GET /api/bi/kpi-summary/
```

**Description**: Get key performance indicators summary

**Parameters**:
- `solution_name` (required): Business solution name
- `period` (optional): Time period
- `kpi_group` (optional): KPI group (financial, operational, customer)

**Example Response**:
```json
{
  "success": true,
  "data": {
    "period": "month",
    "financial_kpis": {
      "total_revenue": {
        "value": 125000,
        "target": 120000,
        "achievement": 104.2,
        "trend": "up",
        "change": 15.5
      },
      "net_profit": {
        "value": 30000,
        "target": 28000,
        "achievement": 107.1,
        "trend": "up",
        "change": 12.3
      },
      "profit_margin": {
        "value": 24.0,
        "target": 23.0,
        "achievement": 104.3,
        "trend": "up",
        "change": 1.0
      }
    },
    "operational_kpis": {
      "total_orders": {
        "value": 147,
        "target": 140,
        "achievement": 105.0,
        "trend": "up",
        "change": 8.5
      },
      "average_order_value": {
        "value": 850,
        "target": 800,
        "achievement": 106.3,
        "trend": "up",
        "change": 6.3
      },
      "inventory_turnover": {
        "value": 4.2,
        "target": 4.0,
        "achievement": 105.0,
        "trend": "up",
        "change": 5.0
      }
    },
    "customer_kpis": {
      "total_customers": {
        "value": 45,
        "target": 40,
        "achievement": 112.5,
        "trend": "up",
        "change": 12.5
      },
      "customer_satisfaction": {
        "value": 4.2,
        "target": 4.0,
        "achievement": 105.0,
        "trend": "up",
        "change": 5.0
      },
      "repeat_customer_rate": {
        "value": 82.2,
        "target": 80.0,
        "achievement": 102.8,
        "trend": "up",
        "change": 2.8
      }
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
| `404` | Not Found | Verify dashboard/report exists |
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

### **Business Performance Monitoring**
1. **Get Analytics**: Use `GET /api/bi/analytics/`
2. **View Dashboards**: Use `GET /api/bi/dashboards/{type}/`
3. **Track KPIs**: Use `GET /api/bi/kpi-summary/`

### **Reporting and Analysis**
1. **Browse Reports**: Use `GET /api/bi/reports/`
2. **Generate Reports**: Use `POST /api/bi/reports/execute/`
3. **Get Sales Data**: Use `GET /api/bi/reports/sales/`
4. **Get Inventory Data**: Use `GET /api/bi/reports/inventory/`

### **Dashboard Management**
1. **List Dashboards**: Use `GET /api/bi/dashboards/`
2. **Get Dashboard Data**: Use `GET /api/bi/dashboards/{type}/`
3. **Get Widgets**: Use `GET /api/bi/dashboards/{id}/widgets/`

## 🔗 **Related Documentation**

- **[Core Operations](01_core_operations.md)** - Core API operations
- **[MSME Features](02_msme_features.md)** - MSME-specific features
- **[Analytics](09_analytics.md)** - Business analytics and dashboards
- **[Authentication](10_authentication.md)** - Authentication details 