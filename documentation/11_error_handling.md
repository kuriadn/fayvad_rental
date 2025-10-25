# Error Handling Guide ⚠️

**Copyright © 2025 Fayvad Digital. All rights reserved.**

## 🎯 **Overview**

This guide provides comprehensive information about error handling across all FBS API endpoints, including error codes, troubleshooting, and resolution steps.

## 📋 **Standard Error Response Format**

All API errors follow a consistent response format:

```json
{
  "success": false,
  "error": "Error description",
  "error_code": "ERROR_CODE",
  "details": {
    "field": "Additional error details",
    "suggestion": "Suggested resolution"
  },
  "timestamp": "2025-01-01T10:00:00Z",
  "request_id": "req_123456789"
}
```

## 🔢 **HTTP Status Codes**

### **2xx Success Codes**
- **200 OK**: Request successful
- **201 Created**: Resource created successfully
- **202 Accepted**: Request accepted for processing

### **4xx Client Error Codes**
- **400 Bad Request**: Invalid request parameters
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **409 Conflict**: Resource conflict
- **422 Unprocessable Entity**: Validation errors
- **429 Too Many Requests**: Rate limit exceeded

### **5xx Server Error Codes**
- **500 Internal Server Error**: Server error
- **502 Bad Gateway**: Gateway error
- **503 Service Unavailable**: Service temporarily unavailable

## 🚨 **Common Error Codes**

### **Authentication Errors**

| Code | Description | Resolution |
|------|-------------|------------|
| `AUTH_001` | Invalid API key | Verify API key is correct |
| `AUTH_002` | Handshake token expired | Create new handshake |
| `AUTH_003` | Invalid handshake token | Verify token format |
| `AUTH_004` | Insufficient permissions | Check user permissions |
| `AUTH_005` | Database access denied | Verify database permissions |

### **Validation Errors**

| Code | Description | Resolution |
|------|-------------|------------|
| `VAL_001` | Missing required field | Include all required fields |
| `VAL_002` | Invalid field format | Check field format/type |
| `VAL_003` | Field value out of range | Use valid value range |
| `VAL_004` | Invalid date format | Use ISO 8601 format |
| `VAL_005` | Duplicate resource | Use unique identifier |

### **Business Logic Errors**

| Code | Description | Resolution |
|------|-------------|------------|
| `BIZ_001` | Solution not found | Verify solution exists |
| `BIZ_002` | Database not ready | Wait for database setup |
| `BIZ_003` | Workflow already exists | Use unique workflow ID |
| `BIZ_004` | Invalid workflow state | Check workflow status |
| `BIZ_005` | Insufficient funds | Check account balance |

### **System Errors**

| Code | Description | Resolution |
|------|-------------|------------|
| `SYS_001` | Database connection failed | Check database status |
| `SYS_002` | External service unavailable | Retry later |
| `SYS_003` | File upload failed | Check file size/format |
| `SYS_004` | Report generation failed | Retry report generation |
| `SYS_005` | Cache operation failed | Retry operation |

## 🔧 **Troubleshooting Guide**

### **Authentication Issues**

**Problem**: `401 Unauthorized`
```json
{
  "success": false,
  "error": "Authentication required",
  "error_code": "AUTH_001",
  "details": {
    "missing": "handshake_token"
  }
}
```

**Resolution**:
1. Create new handshake: `POST /api/auth/handshake/create/`
2. Include token in header: `Authorization: Bearer <token>`
3. Verify token hasn't expired

**Problem**: `403 Forbidden`
```json
{
  "success": false,
  "error": "Insufficient permissions",
  "error_code": "AUTH_004",
  "details": {
    "required": "admin",
    "current": "read"
  }
}
```

**Resolution**:
1. Check user permissions
2. Request elevated permissions
3. Use appropriate API key

### **Validation Issues**

**Problem**: `400 Bad Request`
```json
{
  "success": false,
  "error": "Validation failed",
  "error_code": "VAL_001",
  "details": {
    "missing_fields": ["solution_name", "amount"],
    "invalid_fields": {
      "amount": "Must be positive number"
    }
  }
}
```

**Resolution**:
1. Include all required fields
2. Check field data types
3. Validate field values

### **Rate Limiting**

**Problem**: `429 Too Many Requests`
```json
{
  "success": false,
  "error": "Rate limit exceeded",
  "error_code": "RATE_001",
  "details": {
    "limit": 1000,
    "remaining": 0,
    "reset_time": "2025-01-01T11:00:00Z"
  }
}
```

**Resolution**:
1. Wait for rate limit reset
2. Implement exponential backoff
3. Optimize request frequency

### **Database Issues**

**Problem**: `500 Internal Server Error`
```json
{
  "success": false,
  "error": "Database operation failed",
  "error_code": "SYS_001",
  "details": {
    "operation": "create_solution",
    "database": "fbs_my_business_db"
  }
}
```

**Resolution**:
1. Check database connectivity
2. Verify database permissions
3. Contact support if persistent

## 📞 **Support and Escalation**

### **When to Contact Support**

Contact support when you encounter:
- Persistent `500` errors
- Database connection issues
- Authentication problems that persist
- Rate limiting issues that don't resolve
- Unexpected behavior not covered in this guide

### **Information to Provide**

When contacting support, include:
- Error response (full JSON)
- Request details (endpoint, method, parameters)
- Timestamp of error
- Request ID from error response
- Steps to reproduce
- Environment details

### **Support Channels**

- **Email**: support@fayvad.com
- **Phone**: +1-800-SUPPORT
- **Hours**: 24/7
- **Response Time**: < 4 hours

## 🔄 **Retry Strategies**

### **Exponential Backoff**

For transient errors, implement exponential backoff:

```python
import time
import random

def retry_with_backoff(max_retries=3, base_delay=1):
    for attempt in range(max_retries):
        try:
            # Make API request
            response = make_api_request()
            if response.status_code == 200:
                return response
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            
            # Calculate delay with jitter
            delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
            time.sleep(delay)
```

### **Retryable Errors**

Retry for these error codes:
- `429` (Rate Limited)
- `500` (Server Error)
- `502` (Bad Gateway)
- `503` (Service Unavailable)

### **Non-Retryable Errors**

Do not retry for these error codes:
- `400` (Bad Request)
- `401` (Unauthorized)
- `403` (Forbidden)
- `404` (Not Found)
- `409` (Conflict)

## 📊 **Error Monitoring**

### **Error Tracking**

Monitor these metrics:
- Error rate by endpoint
- Error rate by error code
- Response time trends
- Rate limiting frequency

### **Alerting**

Set up alerts for:
- Error rate > 5%
- Response time > 5 seconds
- Rate limiting frequency > 10/hour
- Authentication failures > 20/hour

## 🔗 **Related Documentation**

- **[Core Operations](01_core_operations.md)** - Core API operations
- **[Authentication](10_authentication.md)** - Authentication details
- **[API Overview](00_api_overview.md)** - Complete API overview 