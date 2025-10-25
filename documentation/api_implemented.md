# FBS API Endpoints - Currently Implemented 📚

**Copyright © 2025 Fayvad Digital. All rights reserved.**

## 🎯 **Overview**

This document provides a comprehensive reference for all currently implemented API endpoints in the FBS system. Each endpoint includes:
- HTTP method and URL
- Expected request parameters and body
- Authentication requirements
- Response format
- Example usage

## 🔐 **Authentication**

All endpoints require authentication using one of these methods:

### **Handshake Authentication (Recommended)**
```http
X-Handshake-Token: <handshake_token>
X-Handshake-Secret: <handshake_secret>
```

### **Legacy Token Authentication**
```http
Authorization: Bearer <odoo_token>
X-Database: <database_name>
```

## 📋 **API Endpoints Reference**

### **1. Core System Endpoints**

#### **1.1 Health Check**
```http
GET /api/health/
```
**Description**: Basic system health check  
**Authentication**: None  
**Response**:
```json
{
  "status": "ok",
  "service": "fbs-api",
  "version": "1.0.0"
}
```

#### **1.2 Generic Model Operations**
```http
GET /api/v1/<model_name>/
POST /api/v1/<model_name>/
GET /api/v1/<model_name>/<id>/
PUT /api/v1/<model_name>/<id>/
PATCH /api/v1/<model_name>/<id>/
DELETE /api/v1/<model_name>/<id>/
POST /api/v1/<model_name>/<id>/<action>/
POST /api/v1/<model_name>/<action>/
POST /api/v1/<model_name>/<id>/<action>/<subaction>/
POST /api/v1/<model_name>/<action>/<subaction>/
```

**Description**: Universal CRUD operations for any Odoo model  
**Authentication**: Required  
**Query Parameters**:
- `domain` (optional): JSON string for filtering records
- `fields` (optional): Comma-separated list of fields to return
- `order` (optional): Field to order by (default: 'id')
- `limit` (optional): Maximum records to return (default: 100, max: 1000)
- `offset` (optional): Number of records to skip (default: 0)

**Request Body (POST/PUT/PATCH)**:
```json
{
  "data": {
    "field1": "value1",
    "field2": "value2"
  }
}
```

**Response**:
```json
{
  "success": true,
  "data": [...],
  "message": "Operation completed successfully"
}
```

### **2. Database Management Endpoints**

#### **2.1 Database Operations**
```http
GET /api/databases/
POST /api/databases/
GET /api/databases/<id>/
PUT /api/databases/<id>/
DELETE /api/databases/<id>/
GET /api/databases/my_databases/
```

**Description**: Manage Odoo database configurations  
**Authentication**: Required  
**Request Body (POST/PUT)**:
```json
{
  "name": "database_name",
  "display_name": "Database Display Name",
  "odoo_db_name": "odoo_database_name",
  "base_url": "http://localhost:8069",
  "description": "Database description",
  "active": true
}
```

#### **2.2 Token Management**
```http
GET /api/tokens/
POST /api/tokens/
GET /api/tokens/<id>/
PUT /api/tokens/<id>/
DELETE /api/tokens/<id>/
```

**Description**: Manage API token mappings  
**Authentication**: Required  
**Request Body (POST/PUT)**:
```json
{
  "database": 1,
  "active": true,
  "expires_at": "2025-12-31T23:59:59Z"
}
```

### **3. Business Logic Endpoints**

#### **3.1 Complex Business Operations**
```http
POST /api/business/complex_operation/
```

**Description**: Execute complex business operations  
**Authentication**: Required  
**Request Body**:
```json
{
  "operation_type": "create_partner_with_address",
  "data": {
    "partner_data": {...},
    "address_data": {...}
  }
}
```

**Valid Operation Types**:
- `create_partner_with_address`
- `book_rental_room`
- `process_payment`

### **4. Profile & Discovery Endpoints**

#### **4.1 Model Profiling**
```http
GET /api/profile/models/
```

**Description**: Get model profiling information with workflows and BI features  
**Authentication**: Required  
**Query Parameters**:
- `model` (optional): Specific model name
- `models` (optional): List of model names

**Response**:
```json
{
  "success": true,
  "data": {
    "models": {...},
    "count": 10,
    "discovery_info": {
      "total_models": 15,
      "filtered_models": 10,
      "has_workflows": true,
      "has_bi_features": true
    }
  }
}
```

#### **4.2 Workflow Discovery**
```http
GET /api/profile/workflows/
```

**Description**: Get workflow discovery information for models  
**Authentication**: Required  
**Query Parameters**:
- `model` (optional): Specific model name

#### **4.3 BI Features Discovery**
```http
GET /api/profile/bi_features/
```

**Description**: Get BI feature discovery information for models  
**Authentication**: Required  
**Query Parameters**:
- `model` (optional): Specific model name

### **5. Onboarding Endpoints**

#### **5.1 Client Onboarding**
```http
POST /api/admin/onboard_client/
```

**Description**: Onboard a new client with database and modules  
**Authentication**: Required  
**Request Body**:
```json
{
  "name": "client_name",
  "database_name": "client_database",
  "modules": ["base", "sale", "product"]
}
```

#### **5.2 Available Modules**
```http
GET /api/admin/available_modules/
```

**Description**: Get list of available Odoo modules  
**Authentication**: Required

#### **5.3 Install Modules**
```http
POST /api/admin/install_modules/
```

**Description**: Install or reinstall modules for a solution database  
**Authentication**: Required  
**Request Body**:
```json
{
  "database_name": "fbs_rental_db",
  "modules": ["base", "web", "mail", "contacts", "hr", "sale", "product", "account", "account_asset", "contract", "maintenance", "stock"]
}
```

### **6. Solution Management Endpoints**

#### **6.1 Install Solution**
```http
POST /api/solutions/install/
```

**Description**: Install a new solution with separate FBS and Django databases  
**Authentication**: Required  
**Request Body**:
```json
{
  "solution_name": "rental",
  "no_odoo_base": false,
  "force": false
}
```

#### **6.2 List Solutions**
```http
GET /api/solutions/
```

**Description**: List all available solutions  
**Authentication**: Required

#### **6.3 Solution Information**
```http
GET /api/solutions/<solution_name>/info/
```

**Description**: Get detailed information about a specific solution  
**Authentication**: Required

#### **6.4 Setup Solution Databases**
```http
POST /api/solutions/<solution_name>/setup_databases/
```

**Description**: Set up databases for a solution  
**Authentication**: Required

#### **6.5 Install Odoo**
```http
POST /api/solutions/<solution_name>/install_odoo/
```

**Description**: Install Odoo in the FBS database for a solution  
**Authentication**: Required

#### **6.6 Delete Solution**
```http
DELETE /api/solutions/<solution_name>/delete/
```

**Description**: Delete a solution and its databases  
**Authentication**: Required  
**Request Body**:
```json
{
  "confirm": true
}
```

### **7. MSME Endpoints**

#### **7.1 MSME Setup and Configuration**
```http
POST /api/msme/setup/
GET /api/msme/dashboard/
GET /api/msme/wizards/
GET /api/msme/templates/
```

**Description**: MSME business setup and configuration  
**Authentication**: Required

#### **7.2 KPI Management**
```http
POST /api/msme/kpis/calculate/
GET /api/msme/kpis/history/
```

**Description**: KPI calculation and history  
**Authentication**: Required

#### **7.3 Compliance Management**
```http
GET /api/msme/compliance/tasks/
POST /api/msme/compliance/create/
```

**Description**: Compliance task management  
**Authentication**: Required

#### **7.4 Marketing Management**
```http
GET /api/msme/marketing/campaigns/
POST /api/msme/marketing/create/
```

**Description**: Marketing campaign management  
**Authentication**: Required

### **8. Client Onboarding Endpoints**

#### **8.1 Onboarding Process**
```http
POST /api/onboarding/start/
GET /api/onboarding/templates/
POST /api/onboarding/configure/
POST /api/onboarding/complete/
GET /api/onboarding/status/
POST /api/onboarding/demo-data/
```

**Description**: Client onboarding and self-service setup  
**Authentication**: Required

### **9. Business Intelligence Endpoints**

#### **9.1 Analytics**
```http
POST /api/bi/analytics/
```

**Description**: Get analytics data  
**Authentication**: Required  
**Request Body**:
```json
{
  "model": "sale.order",
  "report_type": "summary",
  "filters": {},
  "group_by": ["partner_id"],
  "measures": ["amount_total"],
  "date_range": {
    "start": "2025-01-01",
    "end": "2025-12-31"
  }
}
```

#### **9.2 Sales Reports**
```http
POST /api/bi/reports/sales/
```

**Description**: Generate sales reports  
**Authentication**: Required  
**Request Body**:
```json
{
  "period": "month",
  "date_from": "2025-01-01",
  "date_to": "2025-12-31"
}
```

#### **9.3 Inventory Reports**
```http
POST /api/bi/reports/inventory/
```

**Description**: Generate inventory reports  
**Authentication**: Required

#### **9.4 Dashboard Data**
```http
GET /api/bi/dashboards/<dashboard_type>/
```

**Description**: Get dashboard data  
**Authentication**: Required  
**Dashboard Types**: sales, inventory, financial, operations

#### **9.5 KPI Summary**
```http
GET /api/bi/kpi-summary/
```

**Description**: Get KPI summary  
**Authentication**: Required

#### **9.6 Available Reports**
```http
GET /api/bi/reports/
```

**Description**: List available reports  
**Authentication**: Required

#### **9.7 Execute Report**
```http
POST /api/bi/reports/execute/
```

**Description**: Execute a specific report  
**Authentication**: Required  
**Request Body**:
```json
{
  "report_id": 1,
  "parameters": {},
  "format": "json"
}
```

#### **9.8 Available Dashboards**
```http
GET /api/bi/dashboards/
```

**Description**: List available dashboards  
**Authentication**: Required

#### **9.9 Dashboard Widgets**
```http
GET /api/bi/dashboards/<dashboard_id>/widgets/
```

**Description**: Get dashboard widgets  
**Authentication**: Required

### **10. Workflow Endpoints**

#### **10.1 Simple Approval Workflows**
```http
POST /api/workflows/simple/approval/
POST /api/workflows/simple/approve/
POST /api/workflows/simple/reject/
GET /api/workflows/simple/pending/
GET /api/workflows/simple/status/
```

**Description**: Simple approval workflow management  
**Authentication**: Required

#### **10.2 Customer Onboarding Workflow**
```http
POST /api/workflows/simple/customer-onboarding/
```

**Description**: Create customer onboarding workflow  
**Authentication**: Required

#### **10.3 Order Processing Workflow**
```http
POST /api/workflows/simple/order-processing/
```

**Description**: Create order processing workflow  
**Authentication**: Required

#### **10.4 Payment Collection Workflow**
```http
POST /api/workflows/simple/payment-collection/
```

**Description**: Create payment collection workflow  
**Authentication**: Required

#### **10.5 Inventory Management Workflow**
```http
POST /api/workflows/simple/inventory-management/
```

**Description**: Create inventory management workflow  
**Authentication**: Required

### **11. Notification Endpoints**

#### **11.1 MSME Alerts**
```http
GET /api/notifications/alerts/
```

**Description**: Get MSME alerts  
**Authentication**: Required

#### **11.2 Cash Flow Alert**
```http
POST /api/notifications/cash-flow-alert/
```

**Description**: Create cash flow alert  
**Authentication**: Required

#### **11.3 Payment Reminder**
```http
POST /api/notifications/payment-reminder/
```

**Description**: Create payment reminder  
**Authentication**: Required

#### **11.4 Inventory Alert**
```http
POST /api/notifications/inventory-alert/
```

**Description**: Create inventory alert  
**Authentication**: Required

#### **11.5 Compliance Deadline Reminder**
```http
POST /api/notifications/compliance-deadline/
```

**Description**: Create compliance deadline reminder  
**Authentication**: Required

#### **11.6 Customer Follow-up Reminder**
```http
POST /api/notifications/customer-followup/
```

**Description**: Create customer follow-up reminder  
**Authentication**: Required

#### **11.7 Notification Settings**
```http
GET /api/notifications/settings/
POST /api/notifications/settings/update/
```

**Description**: Manage notification settings  
**Authentication**: Required

### **12. Compliance Endpoints**

#### **12.1 Tax Calculation**
```http
POST /api/compliance/calculate-tax/
```

**Description**: Calculate tax  
**Authentication**: Required

#### **12.2 Payroll Basics**
```http
POST /api/compliance/payroll-basics/
```

**Description**: Process payroll basics  
**Authentication**: Required

#### **12.3 Audit Trail**
```http
POST /api/compliance/audit-trail/
GET /api/compliance/audit-trail/get/
```

**Description**: Create and retrieve audit trail  
**Authentication**: Required

#### **12.4 Compliance Deadlines**
```http
POST /api/compliance/deadline/
GET /api/compliance/deadlines/
```

**Description**: Manage compliance deadlines  
**Authentication**: Required

#### **12.5 Regulatory Reports**
```http
POST /api/compliance/regulatory-report/
```

**Description**: Generate regulatory reports  
**Authentication**: Required

#### **12.6 Compliance Summary**
```http
GET /api/compliance/summary/
```

**Description**: Get compliance summary  
**Authentication**: Required

### **13. Accounting Endpoints**

#### **13.1 Cash Basis Entry**
```http
POST /api/accounting/cash-basis-entry/
```

**Description**: Create cash basis entry  
**Authentication**: Required

#### **13.2 Basic Ledger**
```http
GET /api/accounting/basic-ledger/
```

**Description**: Get basic ledger  
**Authentication**: Required

#### **13.3 Income/Expense Tracking**
```http
POST /api/accounting/income-expense/
GET /api/accounting/income-expense-summary/
```

**Description**: Track income and expenses  
**Authentication**: Required

#### **13.4 Basic Reports**
```http
POST /api/accounting/basic-report/
```

**Description**: Generate basic reports  
**Authentication**: Required

#### **13.5 Basic Tax**
```http
POST /api/accounting/basic-tax/
```

**Description**: Calculate basic tax  
**Authentication**: Required

#### **13.6 Cash Position**
```http
GET /api/accounting/cash-position/
```

**Description**: Get cash position  
**Authentication**: Required

#### **13.7 Accounting Summary**
```http
GET /api/accounting/summary/
```

**Description**: Get accounting summary  
**Authentication**: Required

### **15. Maintenance Workflow Endpoints**

#### **15.1 Get Maintenance Request Status**
```http
GET /api/workflows/maintenance/<request_id>/status/
```
**Description**: Get workflow status for a maintenance request  
**Authentication**: Required (Django session)  
**Response**:
```json
{
  "success": true,
  "data": {
    "current_state": "pending",
    "available_events": ["assign_technician", "escalate_priority"],
    "sla_status": {
      "status": "on_track",
      "days_remaining": 5,
      "sla_days": 7
    },
    "workflow_history": [...],
    "workflow_metrics": {...}
  }
}
```

#### **15.2 Perform Maintenance Workflow Action**
```http
POST /api/workflows/maintenance/<request_id>/action/
```
**Description**: Execute workflow actions on maintenance requests  
**Authentication**: Required (Django session)  
**Request Body**:
```json
{
  "action": "assign_technician",
  "data": {
    "technician_name": "John Doe"
  }
}
```

**Available Actions**:
- `assign_technician`: Assign technician to request
- `start_work`: Mark work as started
- `complete_request`: Mark request as completed
- `cancel_request`: Cancel the maintenance request
- `escalate_priority`: Escalate priority level
- `schedule_maintenance`: Schedule maintenance for specific date
- `reopen_request`: Reopen completed/cancelled request

**Example Request**:
```json
{
  "action": "assign_technician",
  "data": {
    "technician_name": "John Doe"
  }
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "assigned_to": "John Doe",
    "assigned_date": "2025-10-20T10:00:00Z",
    "status": "in_progress",
    "workflow_history": [...]
  },
  "message": "Technician assigned successfully"
}
```

#### **15.3 Get Workflow History**
```http
GET /api/workflows/maintenance/<request_id>/history/
```
**Description**: Get complete workflow history for a maintenance request  
**Authentication**: Required (Django session)  
**Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "event_name": "assign_technician",
      "user": "John Doe",
      "timestamp": "2025-10-20T10:00:00Z",
      "notes": "Technician assigned to maintenance request",
      "old_state": "pending",
      "new_state": "in_progress"
    }
  ]
}
```

### **16. Analytics Endpoints**

#### **16.1 Business Overview**
```http
GET /api/analytics/business-overview/
```

**Description**: Get business overview  
**Authentication**: Required

#### **16.2 Daily Cash Position**
```http
GET /api/analytics/daily-cash-position/
```

**Description**: Get daily cash position
**Authentication**: Required

#### **16.3 Sales Summary**
```http
GET /api/analytics/sales-summary/
```

**Description**: Get sales summary
**Authentication**: Required

#### **16.4 Customer Activity**
```http
GET /api/analytics/customer-activity/
```

**Description**: Get customer activity
**Authentication**: Required

#### **16.5 Profit Tracking**
```http
GET /api/analytics/profit-tracking/
```

**Description**: Get profit tracking
**Authentication**: Required

#### **16.6 Inventory Analytics**
```http
GET /api/analytics/inventory-analytics/
```

**Description**: Get inventory analytics
**Authentication**: Required

#### **16.7 Performance Metrics**
```http
GET /api/analytics/performance-metrics/
```

**Description**: Get performance metrics
**Authentication**: Required

#### **16.8 MSME Dashboard**
```http
GET /api/analytics/msme-dashboard/
```

**Description**: Get MSME dashboard
**Authentication**: Required

#### **16.9 Custom Report**
```http
POST /api/analytics/custom-report/
```

**Description**: Generate custom report
**Authentication**: Required

## 📊 **Response Format Standards**

### **Success Response**
```json
{
  "success": true,
  "data": {...},
  "message": "Operation completed successfully"
}
```

### **Error Response**
```json
{
  "success": false,
  "error": "Error description",
  "error_code": "ERROR_CODE",
  "details": {...}
}
```

### **Pagination Response**
```json
{
  "success": true,
  "data": [...],
  "pagination": {
    "count": 100,
    "next": "http://api.fayvad.com/api/endpoint/?page=2",
    "previous": null,
    "page": 1,
    "total_pages": 10
  }
}
```

## 🔧 **Common Query Parameters**

### **Filtering**
- `domain`: JSON string for complex filtering
- `filters`: Simple key-value filters
- `date_from` / `date_to`: Date range filtering

### **Pagination**
- `limit`: Number of records per page (default: 100, max: 1000)
- `offset`: Number of records to skip
- `page`: Page number (alternative to offset)

### **Sorting**
- `order`: Field to order by (prefix with `-` for descending)
- `sort_by`: Alternative sorting parameter

### **Field Selection**
- `fields`: Comma-separated list of fields to return
- `exclude_fields`: Comma-separated list of fields to exclude

## 🚀 **Usage Examples**

### **Example 1: Get Sales Orders**
```bash
curl -X GET "https://api.fayvad.com/api/v1/sale.order/" \
  -H "X-Handshake-Token: your_token" \
  -H "X-Handshake-Secret: your_secret" \
  -H "Content-Type: application/json"
```

### **Example 2: Create a Partner**
```bash
curl -X POST "https://api.fayvad.com/api/v1/res.partner/" \
  -H "X-Handshake-Token: your_token" \
  -H "X-Handshake-Secret: your_secret" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "+1234567890"
    }
  }'
```

### **Example 3: Get Business Overview**
```bash
curl -X GET "https://api.fayvad.com/api/analytics/business-overview/" \
  -H "X-Handshake-Token: your_token" \
  -H "X-Handshake-Secret: your_secret" \
  -H "Content-Type: application/json"
```

## 📝 **Notes**

1. **Authentication**: All endpoints require valid authentication
2. **Database Context**: Most endpoints require database context (provided via handshake or token)
3. **Rate Limiting**: Standard rate limits apply (1000 requests/hour, 100 requests/minute)
4. **Error Handling**: All endpoints return consistent error response format
5. **Caching**: Responses are cached where appropriate for performance
6. **Validation**: All inputs are validated according to serializer specifications

## 🔗 **Related Documentation**

- **[API Overview](00_api_overview.md)** - High-level API overview
- **[Authentication Guide](10_authentication.md)** - Detailed authentication information
- **[Error Handling](11_error_handling.md)** - Error codes and handling
- **[Codebase Review](../CODEBASE_REVIEW_2025.md)** - Technical implementation details
