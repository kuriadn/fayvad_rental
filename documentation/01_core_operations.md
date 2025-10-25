# Core Operations API 📋

**Copyright © 2025 Fayvad Digital. All rights reserved.**

## 🎯 **Overview**

Core operations provide the foundation for all FBS API functionality, including generic model operations, database management, and system administration.

## 🔐 **Authentication**

All endpoints require **Handshake Authentication**:
```bash
Authorization: Bearer <handshake_token>
```

## 📊 **Generic Model Operations**

### **List Records**
```http
GET /api/v1/{model_name}/
```

**Description**: Retrieve records from any Odoo model

**Parameters**:
- `domain` (optional): JSON-encoded domain filter
- `fields` (optional): Comma-separated field list
- `order` (optional): Sort order (default: 'id')
- `limit` (optional): Maximum records (default: 100)
- `offset` (optional): Record offset (default: 0)

**Example Request**:
```bash
curl -X GET "https://api.fayvad.com/api/v1/res.partner/?domain=[('customer','=',True)]&fields=name,email&limit=10" \
  -H "Authorization: Bearer <handshake_token>"
```

**Example Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Customer Name",
      "email": "customer@example.com"
    }
  ],
  "count": 1,
  "total": 1
}
```

### **Get Single Record**
```http
GET /api/v1/{model_name}/{record_id}/
```

**Description**: Retrieve a specific record by ID

**Example Request**:
```bash
curl -X GET "https://api.fayvad.com/api/v1/res.partner/1/" \
  -H "Authorization: Bearer <handshake_token>"
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Customer Name",
    "email": "customer@example.com",
    "phone": "+1234567890"
  }
}
```

### **Create Record**
```http
POST /api/v1/{model_name}/
```

**Description**: Create a new record

**Request Body**:
```json
{
  "name": "New Customer",
  "email": "new@example.com",
  "phone": "+1234567890"
}
```

**Example Request**:
```bash
curl -X POST "https://api.fayvad.com/api/v1/res.partner/" \
  -H "Authorization: Bearer <handshake_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Customer",
    "email": "new@example.com"
  }'
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "id": 2,
    "name": "New Customer",
    "email": "new@example.com"
  },
  "message": "Record created successfully"
}
```

### **Update Record**
```http
PUT /api/v1/{model_name}/{record_id}/
```

**Description**: Update an existing record

**Request Body**:
```json
{
  "name": "Updated Customer Name",
  "email": "updated@example.com"
}
```

**Example Request**:
```bash
curl -X PUT "https://api.fayvad.com/api/v1/res.partner/1/" \
  -H "Authorization: Bearer <handshake_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Customer Name"
  }'
```

### **Partial Update**
```http
PATCH /api/v1/{model_name}/{record_id}/
```

**Description**: Partially update a record

**Request Body**:
```json
{
  "email": "newemail@example.com"
}
```

### **Delete Record**
```http
DELETE /api/v1/{model_name}/{record_id}/
```

**Description**: Delete a record

**Example Request**:
```bash
curl -X DELETE "https://api.fayvad.com/api/v1/res.partner/1/" \
  -H "Authorization: Bearer <handshake_token>"
```

### **Custom Actions**
```http
POST /api/v1/{model_name}/{record_id}/{action}/
POST /api/v1/{model_name}/{action}/
```

**Description**: Execute custom model actions

**Example Request**:
```bash
curl -X POST "https://api.fayvad.com/api/v1/res.partner/1/archive/" \
  -H "Authorization: Bearer <handshake_token>"
```

## 🗄️ **Database Management**

### **List Databases**
```http
GET /api/databases/
```

**Description**: List all databases for the authenticated user

**Example Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "business_db",
      "display_name": "Business Database",
      "odoo_db_name": "fbs_business_db",
      "base_url": "http://localhost:8069",
      "active": true,
      "created_at": "2025-01-01T00:00:00Z"
    }
  ]
}
```

### **Get Database Details**
```http
GET /api/databases/{database_id}/
```

**Description**: Get detailed information about a specific database

### **Create Database**
```http
POST /api/databases/
```

**Description**: Create a new database configuration

**Request Body**:
```json
{
  "name": "new_business",
  "display_name": "New Business Database",
  "odoo_db_name": "fbs_new_business_db",
  "base_url": "http://localhost:8069",
  "description": "Database for new business"
}
```

### **Update Database**
```http
PUT /api/databases/{database_id}/
```

**Description**: Update database configuration

### **Delete Database**
```http
DELETE /api/databases/{database_id}/
```

**Description**: Delete a database configuration

### **My Databases**
```http
GET /api/databases/my_databases/
```

**Description**: Get databases owned by the current user

## 🔑 **Token Management**

### **List Token Mappings**
```http
GET /api/tokens/
```

**Description**: List all token mappings for the user

**Example Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "user": 1,
      "database": 1,
      "odoo_token": "token_hash",
      "odoo_user_id": 1,
      "active": true,
      "expires_at": "2025-12-31T23:59:59Z",
      "last_used": "2025-01-01T12:00:00Z"
    }
  ]
}
```

### **Create Token Mapping**
```http
POST /api/tokens/
```

**Description**: Create a new token mapping

**Request Body**:
```json
{
  "database": 1,
  "odoo_token": "new_token",
  "odoo_user_id": 1
}
```

### **Update Token Mapping**
```http
PUT /api/tokens/{token_id}/
```

**Description**: Update token mapping

### **Delete Token Mapping**
```http
DELETE /api/tokens/{token_id}/
```

**Description**: Delete token mapping

## 🏢 **Business Logic Operations**

### **Complex Operation**
```http
POST /api/business/complex_operation/
```

**Description**: Execute complex business operations

**Request Body**:
```json
{
  "operation_type": "bulk_update",
  "model_name": "res.partner",
  "domain": [("customer", "=", true)],
  "values": {
    "category_id": [1, 2]
  }
}
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "updated_count": 5,
    "operation": "bulk_update",
    "model": "res.partner"
  },
  "message": "Bulk update completed successfully"
}
```

## 👤 **Profile Management**

### **List Models**
```http
GET /api/profile/models/
```

**Description**: Get available Odoo models

**Parameters**:
- `database` (optional): Database name filter
- `model_type` (optional): Filter by model type

**Example Response**:
```json
{
  "success": true,
  "data": [
    {
      "name": "res.partner",
      "display_name": "Contact",
      "description": "Contact and Address Book",
      "fields": [
        {
          "name": "name",
          "type": "char",
          "required": true
        },
        {
          "name": "email",
          "type": "char",
          "required": false
        }
      ]
    }
  ]
}
```

### **List Workflows**
```http
GET /api/profile/workflows/
```

**Description**: Get available workflows

**Example Response**:
```json
{
  "success": true,
  "data": [
    {
      "name": "purchase_approval",
      "display_name": "Purchase Approval",
      "description": "Purchase order approval workflow",
      "states": ["draft", "pending", "approved", "rejected"],
      "transitions": [
        {
          "from": "draft",
          "to": "pending",
          "action": "submit"
        }
      ]
    }
  ]
}
```

### **List BI Features**
```http
GET /api/profile/bi_features/
```

**Description**: Get available business intelligence features

**Example Response**:
```json
{
  "success": true,
  "data": [
    {
      "name": "sales_analytics",
      "display_name": "Sales Analytics",
      "description": "Sales performance analytics",
      "metrics": ["total_sales", "sales_growth", "top_products"],
      "charts": ["line_chart", "bar_chart", "pie_chart"]
    }
  ]
}
```

## 🏥 **Health Checks**

### **Basic Health Check**
```http
GET /api/health/
```

**Description**: Basic system health check

**Example Response**:
```json
{
  "status": "ok",
  "service": "fbs-api",
  "version": "1.0.0",
  "timestamp": "2025-01-01T12:00:00Z"
}
```

### **Detailed Health Check**
```http
GET /api/health/detailed/
```

**Description**: Detailed system health check

**Example Response**:
```json
{
  "status": "ok",
  "service": "fbs-api",
  "version": "1.0.0",
  "timestamp": "2025-01-01T12:00:00Z",
  "components": {
    "database": "healthy",
    "odoo_connection": "healthy",
    "cache": "healthy",
    "authentication": "healthy"
  },
  "uptime": "24h 30m 15s",
  "memory_usage": "45%",
  "cpu_usage": "12%"
}
```

## 🚀 **Solution Management**

### **Install Solution**
```http
POST /api/solutions/install/
```

**Description**: Install a new solution

**Request Body**:
```json
{
  "solution_name": "new_business",
  "business_type": "retail",
  "modules": ["sale", "purchase", "inventory"],
  "demo_data": true
}
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "solution_id": 1,
    "solution_name": "new_business",
    "databases": {
      "odoo": "fbs_new_business_db",
      "django": "djo_new_business_db"
    },
    "status": "installing"
  },
  "message": "Solution installation started"
}
```

### **List Solutions**
```http
GET /api/solutions/list_solutions/
```

**Description**: List all solutions

**Example Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "business_1",
      "status": "active",
      "created_at": "2025-01-01T00:00:00Z",
      "databases": {
        "odoo": "fbs_business_1_db",
        "django": "djo_business_1_db"
      }
    }
  ]
}
```

### **Get Solution Info**
```http
GET /api/solutions/{solution_id}/info/
```

**Description**: Get detailed solution information

### **Setup Solution Databases**
```http
POST /api/solutions/{solution_id}/setup_databases/
```

**Description**: Setup databases for a solution

### **Install Odoo for Solution**
```http
POST /api/solutions/{solution_id}/install_odoo/
```

**Description**: Install Odoo for a specific solution

### **Delete Solution**
```http
DELETE /api/solutions/{solution_id}/delete/
```

**Description**: Delete a solution and its databases

## 🔧 **Error Handling**

### **Common Error Codes**

| Code | Description | Resolution |
|------|-------------|------------|
| `400` | Bad Request | Check request parameters |
| `401` | Unauthorized | Verify authentication token |
| `403` | Forbidden | Check user permissions |
| `404` | Not Found | Verify resource exists |
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

## 🔗 **Related Documentation**

- **[MSME Features](02_msme_features.md)** - MSME-specific operations
- **[Authentication](10_authentication.md)** - Authentication details
- **[Error Handling](11_error_handling.md)** - Comprehensive error guide 