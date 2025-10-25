# Authentication API 🔐

**Copyright © 2025 Fayvad Digital. All rights reserved.**

## 🎯 **Overview**

Authentication provides secure handshake-based authentication for all FBS API endpoints, ensuring secure access to business data and operations.

## 🔑 **Handshake Authentication**

### **Create Handshake**
```http
POST /api/auth/handshake/create/
```

**Description**: Create a new handshake token for API access

**Request Body**:
```json
{
  "api_key": "your_api_key_here",
  "system_name": "your_system_name",
  "solution_name": "rental",
  "permissions": ["read", "write", "admin"],
  "expires_in": 86400
}
```

**Example Response**:
```json
{
  "success": true,
  "handshake": {
    "handshake_id": "uuid",
    "handshake_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "handshake_secret": "secret_key_for_validation",
    "expires_at": "2025-01-02T10:00:00Z",
    "system_name": "fayvad_rentals_django",
    "solution_name": "rental",
    "database_names": {
      "fbs": "fbs_rental_db",
      "django": "djo_rental_db",
      "system": "fbs_system_db"
    },
    "permissions": ["read", "write", "admin"]
  },
  "message": "Handshake created successfully"
}
```

### **Validate Handshake**
```http
POST /api/auth/handshake/validate/
```

**Description**: Validate an existing handshake token

**Request Body**:
```json
{
  "handshake_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "handshake_secret": "secret_key_for_validation"
}
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "valid": true,
    "expires_at": "2025-01-02T10:00:00Z",
    "permissions": ["read", "write", "admin"],
    "database_name": "your_database_name"
  }
}
```

### **Revoke Handshake**
```http
POST /api/auth/handshake/revoke/
```

**Description**: Revoke a handshake token

**Request Body**:
```json
{
  "handshake_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "revoked": true,
    "revoked_at": "2025-01-01T10:00:00Z"
  },
  "message": "Handshake revoked successfully"
}
```

## 🔧 **Error Handling**

### **Common Error Codes**

| Code | Description | Resolution |
|------|-------------|------------|
| `400` | Bad Request | Check request parameters |
| `401` | Unauthorized | Invalid credentials |
| `403` | Forbidden | Insufficient permissions |
| `404` | Not Found | Handshake not found |
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

- **[Core Operations](01_core_operations.md)** - Core API operations
- **[Error Handling](11_error_handling.md)** - Error handling guide 