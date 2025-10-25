# Client Onboarding API 🚀

**Copyright © 2025 Fayvad Digital. All rights reserved.**

## 🎯 **Overview**

Client onboarding provides guided setup for new businesses, including business configuration, template selection, and demo data import to get businesses up and running quickly.

## 🔐 **Authentication**

All endpoints require **Handshake Authentication**:
```bash
Authorization: Bearer <handshake_token>
```

## 🏢 **Business Setup**

### **Start Client Onboarding**
```http
POST /api/onboarding/start/
```

**Description**: Begin the client onboarding process

**Request Body**:
```json
{
  "business_type": "retail",
  "business_name": "My Retail Store",
  "contact_email": "owner@mybusiness.com",
  "contact_phone": "+1234567890",
  "industry": "retail",
  "employee_count": 10,
  "annual_revenue": 500000,
  "preferred_modules": ["sale", "purchase", "inventory"],
  "demo_data": true,
  "setup_assistance": true
}
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "onboarding_id": "onboard_123",
    "business_name": "My Retail Store",
    "business_type": "retail",
    "status": "initialized",
    "solution_name": "my_retail_store",
    "next_steps": [
      {
        "step": 1,
        "title": "Select Business Template",
        "description": "Choose a pre-configured business template",
        "required": true,
        "estimated_time": "5 minutes"
      },
      {
        "step": 2,
        "title": "Configure Business Details",
        "description": "Set up your business information",
        "required": true,
        "estimated_time": "10 minutes"
      }
    ],
    "estimated_completion": "30 minutes"
  },
  "message": "Onboarding process started successfully"
}
```

### **Get Onboarding Templates**
```http
GET /api/onboarding/templates/
```

**Description**: Get available business templates for onboarding

**Parameters**:
- `business_type` (optional): Filter by business type
- `industry` (optional): Filter by industry
- `employee_count` (optional): Filter by employee count range

**Example Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": "retail_basic",
      "name": "Basic Retail Template",
      "business_type": "retail",
      "industry": "retail",
      "description": "Standard retail business setup with essential features",
      "features": [
        "Sales management",
        "Inventory tracking",
        "Customer management",
        "Basic reporting"
      ],
      "modules": ["sale", "purchase", "inventory", "account"],
      "chart_of_accounts": "retail_coa",
      "product_categories": ["electronics", "clothing", "home"],
      "demo_data": true,
      "estimated_setup_time": "30 minutes",
      "monthly_cost": 99
    },
    {
      "id": "retail_premium",
      "name": "Premium Retail Template",
      "business_type": "retail",
      "industry": "retail",
      "description": "Advanced retail setup with marketing and analytics",
      "features": [
        "All basic features",
        "Marketing campaigns",
        "Advanced analytics",
        "Multi-location support"
      ],
      "modules": ["sale", "purchase", "inventory", "account", "marketing", "analytics"],
      "chart_of_accounts": "retail_premium_coa",
      "product_categories": ["electronics", "clothing", "home", "sports", "books"],
      "demo_data": true,
      "estimated_setup_time": "45 minutes",
      "monthly_cost": 199
    }
  ]
}
```

### **Configure Business Setup**
```http
POST /api/onboarding/configure/
```

**Description**: Configure business setup with selected template

**Request Body**:
```json
{
  "onboarding_id": "onboard_123",
  "template_id": "retail_basic",
  "business_config": {
    "business_name": "My Retail Store",
    "business_address": "123 Main St, City, State 12345",
    "tax_id": "12-3456789",
    "business_license": "BL123456",
    "bank_account": {
      "bank_name": "Local Bank",
      "account_number": "1234567890",
      "routing_number": "123456789"
    }
  },
  "customization": {
    "product_categories": ["electronics", "clothing", "home", "sports"],
    "payment_methods": ["cash", "credit_card", "bank_transfer"],
    "shipping_methods": ["standard", "express", "pickup"],
    "tax_rates": {
      "state_tax": 6.5,
      "local_tax": 1.0
    }
  },
  "demo_data": {
    "include_products": true,
    "include_customers": true,
    "include_suppliers": true,
    "include_initial_sales": true
  }
}
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "onboarding_id": "onboard_123",
    "status": "configuring",
    "progress": 60,
    "current_step": "database_setup",
    "estimated_remaining": "15 minutes",
    "setup_details": {
      "template_applied": "retail_basic",
      "modules_installing": ["sale", "purchase", "inventory"],
      "customizations_applied": true,
      "demo_data_queued": true
    }
  },
  "message": "Business configuration applied successfully"
}
```

### **Complete Onboarding**
```http
POST /api/onboarding/complete/
```

**Description**: Complete the onboarding process

**Request Body**:
```json
{
  "onboarding_id": "onboard_123",
  "final_confirmation": true,
  "additional_requirements": [
    "custom_integration",
    "advanced_reporting",
    "mobile_app_access"
  ]
}
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "onboarding_id": "onboard_123",
    "status": "completed",
    "solution_name": "my_retail_store",
    "access_credentials": {
      "admin_username": "admin",
      "admin_password": "temporary_password",
      "api_key": "api_key_123",
      "database_name": "fbs_my_retail_store_db"
    },
    "next_steps": [
      "Change default password",
      "Import your actual data",
      "Configure payment gateways",
      "Set up user accounts"
    ],
    "support_contact": {
      "email": "support@fayvad.com",
      "phone": "+1-800-SUPPORT",
      "hours": "24/7"
    }
  },
  "message": "Onboarding completed successfully! Your business is ready to use."
}
```

### **Get Onboarding Status**
```http
GET /api/onboarding/status/
```

**Description**: Get current onboarding status and progress

**Parameters**:
- `onboarding_id` (required): Onboarding process ID

**Example Response**:
```json
{
  "success": true,
  "data": {
    "onboarding_id": "onboard_123",
    "business_name": "My Retail Store",
    "status": "configuring",
    "progress": 75,
    "current_step": "demo_data_import",
    "started_at": "2025-01-01T10:00:00Z",
    "estimated_completion": "2025-01-01T10:30:00Z",
    "completed_steps": [
      {
        "step": 1,
        "title": "Select Business Template",
        "completed_at": "2025-01-01T10:05:00Z"
      },
      {
        "step": 2,
        "title": "Configure Business Details",
        "completed_at": "2025-01-01T10:15:00Z"
      }
    ],
    "remaining_steps": [
      {
        "step": 3,
        "title": "Import Demo Data",
        "estimated_time": "10 minutes"
      },
      {
        "step": 4,
        "title": "Final Configuration",
        "estimated_time": "5 minutes"
      }
    ]
  }
}
```

### **Import Demo Data**
```http
POST /api/onboarding/demo-data/
```

**Description**: Import demo data for the business

**Request Body**:
```json
{
  "onboarding_id": "onboard_123",
  "demo_data_config": {
    "products": {
      "count": 50,
      "categories": ["electronics", "clothing", "home"],
      "include_images": true,
      "include_pricing": true
    },
    "customers": {
      "count": 25,
      "include_contact_info": true,
      "include_purchase_history": true
    },
    "suppliers": {
      "count": 10,
      "include_contact_info": true,
      "include_product_catalog": true
    },
    "sales": {
      "count": 100,
      "date_range": {
        "start": "2024-01-01",
        "end": "2024-12-31"
      },
      "include_payments": true
    },
    "inventory": {
      "include_stock_levels": true,
      "include_movements": true
    }
  }
}
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "onboarding_id": "onboard_123",
    "status": "importing_demo_data",
    "progress": 85,
    "import_summary": {
      "products_imported": 50,
      "customers_imported": 25,
      "suppliers_imported": 10,
      "sales_imported": 100,
      "inventory_records": 150
    },
    "estimated_completion": "5 minutes"
  },
  "message": "Demo data import started successfully"
}
```

## 🔧 **Error Handling**

### **Common Error Codes**

| Code | Description | Resolution |
|------|-------------|------------|
| `400` | Bad Request | Check request parameters |
| `401` | Unauthorized | Verify authentication token |
| `403` | Forbidden | Check user permissions |
| `404` | Not Found | Verify onboarding ID exists |
| `409` | Conflict | Onboarding already in progress |
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

## 🎯 **Onboarding Flow**

### **Complete Onboarding Process**

1. **Start Onboarding** (`POST /api/onboarding/start/`)
   - Provide business information
   - Get onboarding ID

2. **Select Template** (`GET /api/onboarding/templates/`)
   - Browse available templates
   - Choose appropriate template

3. **Configure Business** (`POST /api/onboarding/configure/`)
   - Apply template configuration
   - Customize business settings

4. **Import Demo Data** (`POST /api/onboarding/demo-data/`)
   - Import sample data
   - Configure initial setup

5. **Complete Setup** (`POST /api/onboarding/complete/`)
   - Finalize configuration
   - Get access credentials

6. **Monitor Progress** (`GET /api/onboarding/status/`)
   - Track setup progress
   - Get estimated completion

### **Typical Timeline**

| Step | Duration | Description |
|------|----------|-------------|
| 1 | 5 minutes | Business information collection |
| 2 | 5 minutes | Template selection |
| 3 | 10 minutes | Business configuration |
| 4 | 15 minutes | Demo data import |
| 5 | 5 minutes | Final setup |
| **Total** | **40 minutes** | Complete onboarding |

## 🎯 **Use Cases**

### **New Business Setup**
1. **Start Onboarding**: Use `POST /api/onboarding/start/`
2. **Select Template**: Use `GET /api/onboarding/templates/`
3. **Configure Business**: Use `POST /api/onboarding/configure/`
4. **Import Demo Data**: Use `POST /api/onboarding/demo-data/`
5. **Complete Setup**: Use `POST /api/onboarding/complete/`

### **Template Customization**
1. **Browse Templates**: Use `GET /api/onboarding/templates/`
2. **Apply Configuration**: Use `POST /api/onboarding/configure/`
3. **Monitor Progress**: Use `GET /api/onboarding/status/`

### **Demo Data Management**
1. **Configure Demo Data**: Use `POST /api/onboarding/demo-data/`
2. **Monitor Import**: Use `GET /api/onboarding/status/`

## 🔗 **Related Documentation**

- **[Core Operations](01_core_operations.md)** - Core API operations
- **[MSME Features](02_msme_features.md)** - MSME-specific features
- **[Analytics](09_analytics.md)** - Business analytics and dashboards
- **[Authentication](10_authentication.md)** - Authentication details 