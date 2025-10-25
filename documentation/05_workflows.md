# Simplified Workflows API 🔄

**Copyright © 2025 Fayvad Digital. All rights reserved.**

## 🎯 **Overview**

Simplified workflows provide streamlined business process automation for MSMEs, including approval workflows, customer onboarding, order processing, payment collection, and inventory management.

## 🔐 **Authentication**

All endpoints require **Handshake Authentication**:
```bash
Authorization: Bearer <handshake_token>
```

## ✅ **Approval Workflows**

### **Create Simple Approval Workflow**
```http
POST /api/workflows/simple/approval/
```

**Description**: Create a simple approval workflow

**Request Body**:
```json
{
  "solution_name": "my_business",
  "workflow_type": "purchase_approval",
  "title": "Purchase Order Approval",
  "description": "Approval for purchase order PO-001",
  "amount": 5000,
  "requestor": "john.doe",
  "approvers": ["manager1", "finance1"],
  "priority": "medium",
  "deadline": "2025-01-31T23:59:59Z",
  "attachments": [
    {
      "name": "purchase_order.pdf",
      "url": "https://example.com/po-001.pdf"
    }
  ]
}
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "workflow_id": "wf_123",
    "workflow_type": "purchase_approval",
    "title": "Purchase Order Approval",
    "status": "pending",
    "current_step": "manager_approval",
    "requestor": "john.doe",
    "approvers": ["manager1", "finance1"],
    "created_at": "2025-01-01T10:00:00Z",
    "deadline": "2025-01-31T23:59:59Z",
    "progress": 0
  },
  "message": "Approval workflow created successfully"
}
```

### **Approve Workflow Step**
```http
POST /api/workflows/simple/approve/
```

**Description**: Approve a workflow step

**Request Body**:
```json
{
  "workflow_id": "wf_123",
  "approver": "manager1",
  "decision": "approved",
  "comments": "Purchase order looks good, approved for processing",
  "next_approver": "finance1"
}
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "workflow_id": "wf_123",
    "status": "pending",
    "current_step": "finance_approval",
    "approved_by": "manager1",
    "approved_at": "2025-01-01T11:00:00Z",
    "progress": 50,
    "next_approver": "finance1"
  },
  "message": "Workflow step approved successfully"
}
```

### **Reject Workflow Step**
```http
POST /api/workflows/simple/reject/
```

**Description**: Reject a workflow step

**Request Body**:
```json
{
  "workflow_id": "wf_123",
  "approver": "manager1",
  "decision": "rejected",
  "comments": "Budget exceeded, please revise the purchase order",
  "return_to": "john.doe"
}
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "workflow_id": "wf_123",
    "status": "rejected",
    "rejected_by": "manager1",
    "rejected_at": "2025-01-01T11:00:00Z",
    "comments": "Budget exceeded, please revise the purchase order",
    "returned_to": "john.doe"
  },
  "message": "Workflow step rejected"
}
```

### **Get Pending Workflows**
```http
GET /api/workflows/simple/pending/
```

**Description**: Get pending workflows for the user

**Parameters**:
- `solution_name` (required): Business solution name
- `user` (optional): Filter by user
- `workflow_type` (optional): Filter by workflow type
- `priority` (optional): Filter by priority

**Example Response**:
```json
{
  "success": true,
  "data": [
    {
      "workflow_id": "wf_123",
      "workflow_type": "purchase_approval",
      "title": "Purchase Order Approval",
      "status": "pending",
      "current_step": "manager_approval",
      "requestor": "john.doe",
      "amount": 5000,
      "priority": "medium",
      "created_at": "2025-01-01T10:00:00Z",
      "deadline": "2025-01-31T23:59:59Z",
      "progress": 0
    },
    {
      "workflow_id": "wf_124",
      "workflow_type": "expense_approval",
      "title": "Expense Report Approval",
      "status": "pending",
      "current_step": "finance_approval",
      "requestor": "jane.smith",
      "amount": 2500,
      "priority": "high",
      "created_at": "2025-01-01T09:00:00Z",
      "deadline": "2025-01-15T23:59:59Z",
      "progress": 50
    }
  ]
}
```

### **Get Workflow Status**
```http
GET /api/workflows/simple/status/
```

**Description**: Get workflow status and details

**Parameters**:
- `workflow_id` (required): Workflow ID

**Example Response**:
```json
{
  "success": true,
  "data": {
    "workflow_id": "wf_123",
    "workflow_type": "purchase_approval",
    "title": "Purchase Order Approval",
    "status": "pending",
    "current_step": "finance_approval",
    "requestor": "john.doe",
    "approvers": ["manager1", "finance1"],
    "amount": 5000,
    "priority": "medium",
    "created_at": "2025-01-01T10:00:00Z",
    "deadline": "2025-01-31T23:59:59Z",
    "progress": 50,
    "history": [
      {
        "step": "manager_approval",
        "approver": "manager1",
        "decision": "approved",
        "comments": "Purchase order looks good",
        "timestamp": "2025-01-01T11:00:00Z"
      }
    ],
    "attachments": [
      {
        "name": "purchase_order.pdf",
        "url": "https://example.com/po-001.pdf"
      }
    ]
  }
}
```

## 👥 **Customer Onboarding Workflows**

### **Create Customer Onboarding Workflow**
```http
POST /api/workflows/simple/customer-onboarding/
```

**Description**: Create a customer onboarding workflow

**Request Body**:
```json
{
  "solution_name": "my_business",
  "customer_name": "ABC Company",
  "contact_person": "John Smith",
  "email": "john@abc.com",
  "phone": "+1234567890",
  "business_type": "retail",
  "expected_volume": "medium",
  "credit_limit": 10000,
  "onboarding_steps": [
    "customer_verification",
    "credit_check",
    "account_setup",
    "welcome_kit"
  ]
}
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "workflow_id": "wf_125",
    "workflow_type": "customer_onboarding",
    "customer_name": "ABC Company",
    "status": "in_progress",
    "current_step": "customer_verification",
    "progress": 25,
    "steps": [
      {
        "step": "customer_verification",
        "status": "in_progress",
        "assigned_to": "sales_team",
        "due_date": "2025-01-03T23:59:59Z"
      },
      {
        "step": "credit_check",
        "status": "pending",
        "assigned_to": "finance_team",
        "due_date": "2025-01-05T23:59:59Z"
      }
    ],
    "created_at": "2025-01-01T10:00:00Z",
    "estimated_completion": "2025-01-07T23:59:59Z"
  },
  "message": "Customer onboarding workflow created successfully"
}
```

## 📦 **Order Processing Workflows**

### **Create Order Processing Workflow**
```http
POST /api/workflows/simple/order-processing/
```

**Description**: Create an order processing workflow

**Request Body**:
```json
{
  "solution_name": "my_business",
  "order_id": "ORD-001",
  "customer_name": "ABC Company",
  "order_items": [
    {
      "product": "Product A",
      "quantity": 10,
      "unit_price": 100,
      "total": 1000
    }
  ],
  "total_amount": 1000,
  "shipping_address": "123 Main St, City, State 12345",
  "payment_method": "credit_card",
  "priority": "normal"
}
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "workflow_id": "wf_126",
    "workflow_type": "order_processing",
    "order_id": "ORD-001",
    "status": "processing",
    "current_step": "payment_verification",
    "customer_name": "ABC Company",
    "total_amount": 1000,
    "progress": 25,
    "steps": [
      {
        "step": "payment_verification",
        "status": "in_progress",
        "assigned_to": "finance_team",
        "due_date": "2025-01-01T12:00:00Z"
      },
      {
        "step": "inventory_check",
        "status": "pending",
        "assigned_to": "warehouse_team",
        "due_date": "2025-01-01T14:00:00Z"
      }
    ],
    "created_at": "2025-01-01T10:00:00Z",
    "estimated_completion": "2025-01-02T10:00:00Z"
  },
  "message": "Order processing workflow created successfully"
}
```

## 💰 **Payment Collection Workflows**

### **Create Payment Collection Workflow**
```http
POST /api/workflows/simple/payment-collection/
```

**Description**: Create a payment collection workflow

**Request Body**:
```json
{
  "solution_name": "my_business",
  "invoice_id": "INV-001",
  "customer_name": "ABC Company",
  "amount": 5000,
  "due_date": "2025-01-31T23:59:59Z",
  "payment_terms": "net_30",
  "collection_steps": [
    "payment_reminder",
    "follow_up_call",
    "payment_plan",
    "legal_action"
  ]
}
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "workflow_id": "wf_127",
    "workflow_type": "payment_collection",
    "invoice_id": "INV-001",
    "status": "active",
    "current_step": "payment_reminder",
    "customer_name": "ABC Company",
    "amount": 5000,
    "due_date": "2025-01-31T23:59:59Z",
    "progress": 25,
    "steps": [
      {
        "step": "payment_reminder",
        "status": "in_progress",
        "assigned_to": "accounts_receivable",
        "due_date": "2025-01-15T23:59:59Z"
      },
      {
        "step": "follow_up_call",
        "status": "pending",
        "assigned_to": "collections_team",
        "due_date": "2025-01-25T23:59:59Z"
      }
    ],
    "created_at": "2025-01-01T10:00:00Z"
  },
  "message": "Payment collection workflow created successfully"
}
```

## 📦 **Inventory Management Workflows**

### **Create Inventory Management Workflow**
```http
POST /api/workflows/simple/inventory-management/
```

**Description**: Create an inventory management workflow

**Request Body**:
```json
{
  "solution_name": "my_business",
  "workflow_type": "stock_replenishment",
  "product_id": "PROD-001",
  "product_name": "Product A",
  "current_stock": 5,
  "min_stock": 20,
  "reorder_quantity": 50,
  "supplier": "Supplier XYZ",
  "urgency": "high",
  "estimated_cost": 2500
}
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "workflow_id": "wf_128",
    "workflow_type": "stock_replenishment",
    "product_id": "PROD-001",
    "product_name": "Product A",
    "status": "pending_approval",
    "current_step": "manager_approval",
    "current_stock": 5,
    "min_stock": 20,
    "reorder_quantity": 50,
    "urgency": "high",
    "progress": 0,
    "steps": [
      {
        "step": "manager_approval",
        "status": "pending",
        "assigned_to": "inventory_manager",
        "due_date": "2025-01-02T23:59:59Z"
      },
      {
        "step": "purchase_order",
        "status": "pending",
        "assigned_to": "procurement_team",
        "due_date": "2025-01-03T23:59:59Z"
      }
    ],
    "created_at": "2025-01-01T10:00:00Z"
  },
  "message": "Inventory management workflow created successfully"
}
```

## 🔧 **Error Handling**

### **Common Error Codes**

| Code | Description | Resolution |
|------|-------------|------------|
| `400` | Bad Request | Check request parameters |
| `401` | Unauthorized | Verify authentication token |
| `403` | Forbidden | Check user permissions |
| `404` | Not Found | Verify workflow exists |
| `409` | Conflict | Workflow already exists |
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

### **Approval Management**
1. **Create Approval**: Use `POST /api/workflows/simple/approval/`
2. **Approve Step**: Use `POST /api/workflows/simple/approve/`
3. **Reject Step**: Use `POST /api/workflows/simple/reject/`
4. **Check Status**: Use `GET /api/workflows/simple/status/`

### **Customer Management**
1. **Onboard Customer**: Use `POST /api/workflows/simple/customer-onboarding/`
2. **Track Progress**: Use `GET /api/workflows/simple/status/`

### **Order Processing**
1. **Process Order**: Use `POST /api/workflows/simple/order-processing/`
2. **Track Status**: Use `GET /api/workflows/simple/status/`

### **Payment Collection**
1. **Collect Payment**: Use `POST /api/workflows/simple/payment-collection/`
2. **Monitor Progress**: Use `GET /api/workflows/simple/status/`

### **Inventory Management**
1. **Manage Stock**: Use `POST /api/workflows/simple/inventory-management/`
2. **Track Replenishment**: Use `GET /api/workflows/simple/status/`

## 🔗 **Related Documentation**

- **[Core Operations](01_core_operations.md)** - Core API operations
- **[MSME Features](02_msme_features.md)** - MSME-specific features
- **[Notifications](06_notifications.md)** - Notification system
- **[Authentication](10_authentication.md)** - Authentication details 