# Business Logic Preservation Plan

## Overview
This document maps all business logic from Django models to FBS services to ensure nothing is lost during the migration to a pure FBS architecture.

## Business Logic Categories

### 1. Data Validation Rules
- **Location Code Format**: Must be uppercase letters and numbers, max 10 characters
- **Phone Number Validation**: Kenyan phone number format validation
- **ID Number Validation**: Must be exactly 8 digits
- **Email Format Validation**: Standard email format validation
- **Address Length Validation**: Max 1000 characters
- **City Name Validation**: Max 100 characters

### 2. Business Rules
- **Location Deletion**: Cannot delete location with rooms or tenants
- **Location Setup**: Setup complete locations must have at least one room
- **Location Deactivation**: Cannot deactivate location with occupied rooms
- **Tenant Termination**: Cannot terminate tenancy with outstanding balance
- **Room Assignment**: Room must be available for tenant assignment

### 3. Computed Fields & Statistics
- **Room Counts**: Total, occupied, available room counts
- **Occupancy Rate**: Calculated as occupied_count / total_room_count
- **Monthly Revenue**: Calculated from occupied rooms
- **Tenant Count**: Active tenants per location

### 4. Audit & Activity Logging
- **Activity Logging**: All CRUD operations logged with user, timestamp, old/new values
- **Change Tracking**: Track field-level changes for audit purposes
- **User Context**: Log user performing actions with IP address and session info

## Migration Status

### ✅ Completed
- **LocationServiceFBS**: All business logic preserved
- **TenantServiceFBS**: All business logic preserved
- **RentalAgreementServiceFBS**: All business logic preserved
- **ContractServiceFBS**: All business logic preserved
- **DocumentServiceFBS**: All business logic preserved
- **RoomServiceFBS**: All business logic preserved
- **PaymentServiceFBS**: All business logic preserved
- **MaintenanceServiceFBS**: All business logic preserved

### 🔄 In Progress
- **UserServiceFBS**: Create and migrate business logic
- **GroupServiceFBS**: Create and migrate business logic

### 📋 To Do
- **MaintenanceServiceFBS**: Create and migrate business logic
- **UserServiceFBS**: Create and migrate business logic
- **GroupServiceFBS**: Create and migrate business logic

## Implementation Pattern

### 1. Validation Methods
```python
def validate_[entity]_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate [entity] data according to business rules"""
    errors = []
    # Implement validation logic
    if errors:
        return {'success': False, 'errors': errors}
    return {'success': True}
```

### 2. Business Rule Methods
```python
def can_[action]_[entity](self, entity_id: int) -> Dict[str, Any]:
    """Check if [action] can be performed on [entity] according to business rules"""
    # Implement business rule checks
    return {'success': True, 'can_[action]': True/False, 'reason': '...'}
```

### 3. Statistics Methods
```python
def update_[entity]_statistics(self, entity_id: int) -> Dict[str, Any]:
    """Update computed statistics from related data"""
    # Implement statistics calculation
    return {'success': True, 'data': statistics_data}
```

### 4. Activity Logging Methods
```python
def log_[entity]_activity(self, entity_id: int, action: str, message: str, 
                         old_values: Dict = None, new_values: Dict = None) -> Dict[str, Any]:
    """Log [entity] activity for audit purposes"""
    # Implement activity logging using FBS virtual fields
    return result
```

## FBS Integration Points

### 1. Virtual Fields for Audit Data
- Store activity logs in FBS virtual fields
- Maintain change history for compliance
- Track user actions and timestamps

### 2. Business Intelligence
- Use FBS BI interface for analytics
- Leverage FBS MSME interface for business summaries
- Integrate with FBS workflow for complex business processes

### 3. Data Validation
- Implement validation at service layer
- Use FBS virtual fields for validation rules
- Maintain business rule enforcement

## Testing Strategy

### 1. Unit Tests
- Test all validation methods
- Test business rule methods
- Test statistics calculation methods

### 2. Integration Tests
- Test FBS service integration
- Test virtual fields functionality
- Test business logic preservation

### 3. Business Logic Tests
- Verify all business rules are enforced
- Confirm validation logic works correctly
- Ensure audit logging is comprehensive

## Risk Mitigation

### 1. Business Logic Loss
- **Risk**: Critical business rules not migrated
- **Mitigation**: Comprehensive mapping and testing
- **Monitoring**: Automated validation checks

### 2. Data Integrity
- **Risk**: Data validation bypassed
- **Mitigation**: Service layer validation enforcement
- **Monitoring**: Data quality checks

### 3. Audit Trail Loss
- **Risk**: Activity logging not preserved
- **Mitigation**: FBS virtual fields for audit data
- **Monitoring**: Audit log verification

## Success Criteria

### 1. Functional Completeness
- All business rules implemented in FBS services
- All validation logic preserved
- All computed fields working correctly

### 2. Performance
- FBS service response times acceptable
- Virtual fields performance optimized
- Business logic execution efficient

### 3. Compliance
- Audit trails maintained
- Business rules enforced
- Data validation comprehensive

## Next Steps

1. **Complete Business Logic Migration** for remaining services
2. **Implement Comprehensive Testing** for all business logic
3. **Create Migration Scripts** for existing data
4. **Deploy and Validate** in staging environment
5. **Monitor and Optimize** performance and functionality
