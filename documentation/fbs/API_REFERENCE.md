# FBS API Reference

## Overview

This document provides a complete reference for all **FBS (Fayvad Business Suite)** service interfaces. FBS uses service interfaces rather than REST API endpoints, providing maximum performance and flexibility.

## Table of Contents

1. [FBSInterface](#fbsinterface) - Main entry point
2. [OdooIntegrationInterface](#odoointegrationinterface) - Odoo ERP integration
3. [VirtualFieldsInterface](#virtualfieldsinterface) - Custom field management
4. [MSMEInterface](#msmeinterface) - MSME business management
5. [BusinessIntelligenceInterface](#businessintelligenceinterface) - BI and analytics
6. [WorkflowInterface](#workflowinterface) - Workflow management
7. [AccountingInterface](#accountinginterface) - Financial operations
8. [CacheInterface](#cacheinterface) - Caching system
9. [Response Format](#response-format) - Standard response structure

## FBSInterface

The main interface for accessing all FBS capabilities.

### **Constructor**

```python
FBSInterface(solution_name: str, license_key: str = None)
```

**Parameters:**
- `solution_name` (str): Unique identifier for the business solution
- `license_key` (str, optional): License key for feature control

### **Methods**

#### **get_solution_info()**
Returns information about the current solution.

**Returns:** `Dict[str, Any]`
```python
{
    'solution_name': 'your_solution_name',
    'timestamp': '2025-01-15T10:30:00Z',
    'capabilities': {
        'msme': 'MSME business management',
        'accounting': 'Simple accounting operations',
        'bi': 'Business Intelligence & Analytics',
        'workflows': 'Workflow management',
        'compliance': 'Compliance management',
        'notifications': 'Notification system',
        'onboarding': 'Client onboarding',
        'odoo': 'Odoo ERP integration',
        'fields': 'Virtual fields & custom data',
        'cache': 'Cache management'
    }
}
```

#### **get_system_health()**
Returns the health status of all FBS services.

**Returns:** `Dict[str, Any]`
```python
{
    'solution_name': 'your_solution_name',
    'status': 'healthy',
    'timestamp': '2025-01-15T10:30:00Z',
    'services': {
        'msme': 'operational',
        'accounting': 'operational',
        'bi': 'operational',
        'workflows': 'operational',
        'compliance': 'operational',
        'notifications': 'operational',
        'onboarding': 'operational',
        'odoo': 'operational',
        'fields': 'operational',
        'cache': 'operational'
    }
}
```

#### **get_license_info()**
Returns comprehensive license information.

**Returns:** `Dict[str, Any]`
```python
{
    'license_type': 'professional',
    'status': 'active',
    'features': ['msme', 'bi', 'workflows', 'dms'],
    'limits': {
        'msme_businesses': 10,
        'workflows': 50,
        'reports': 1000,
        'users': 25,
        'documents': 5000,
        'storage_gb': 100
    },
    'expiry_date': '2025-12-31',
    'source': 'license_manager'
}
```

#### **get_odoo_client()**
Returns the underlying Odoo client for direct access.

**Returns:** `OdooClient`

#### **is_odoo_available()**
Checks if Odoo integration is available.

**Returns:** `bool`

#### **check_feature_access(feature_name: str, **kwargs)**
Checks if user can access a specific feature.

**Parameters:**
- `feature_name` (str): Name of the feature to check
- `**kwargs`: Additional parameters (e.g., `current_usage`)

**Returns:** `Dict[str, Any]`
```python
{
    'access': True,
    'remaining': 5,
    'limit': 10,
    'feature_name': 'msme_businesses',
    'licensing_available': True
}
```

#### **get_upgrade_prompt(feature_name: str)**
Returns upgrade prompt for a feature.

**Parameters:**
- `feature_name` (str): Name of the feature

**Returns:** `Dict[str, Any]`
```python
{
    'upgrade_required': True,
    'message': 'Upgrade to Professional plan for more MSME businesses',
    'current_plan': 'basic',
    'recommended_plan': 'professional',
    'feature_limits': {
        'basic': 3,
        'professional': 10,
        'enterprise': 100
    }
}
```

#### **get_feature_matrix()**
Returns complete feature availability matrix.

**Returns:** `Dict[str, Dict[str, Any]]`
```python
{
    'msme': {
        'enabled': True,
        'limit': 10,
        'unlimited': False,
        'dependencies_met': True,
        'missing_dependencies': []
    },
    'bi': {
        'enabled': True,
        'limit': 1000,
        'unlimited': False,
        'dependencies_met': True,
        'missing_dependencies': []
    }
}
```

#### **get_upgrade_analysis()**
Returns comprehensive upgrade analysis.

**Returns:** `Dict[str, Any]`
```python
{
    'analysis': {
        'current_usage': {
            'msme_businesses': 8,
            'workflows': 25,
            'reports': 500
        },
        'recommendations': [
            {
                'feature': 'msme_businesses',
                'current_plan': 'basic',
                'recommended_plan': 'professional',
                'reason': '80% of limit reached'
            }
        ],
        'cost_analysis': {
            'basic_monthly': 99,
            'professional_monthly': 199,
            'savings': 'Better value for growing businesses'
        }
    }
}
```

## OdooIntegrationInterface

Provides complete access to Odoo ERP functionality.

### **Constructor**

```python
OdooIntegrationInterface(solution_name: str)
```

### **Methods**

#### **discover_models(database_name: Optional[str] = None)**
Discovers available Odoo models.

**Parameters:**
- `database_name` (str, optional): Specific database to query

**Returns:** `Dict[str, Any]`
```python
{
    'success': True,
    'data': [
        {
            'name': 'res.partner',
            'display_name': 'Contact',
            'description': 'Contact and Address',
            'fields_count': 45
        }
    ]
}
```

#### **discover_fields(model_name: str, database_name: Optional[str] = None)**
Discovers fields for a specific Odoo model.

**Parameters:**
- `model_name` (str): Name of the Odoo model
- `database_name` (str, optional): Specific database to query

**Returns:** `Dict[str, Any]`
```python
{
    'success': True,
    'data': [
        {
            'name': 'name',
            'display_name': 'Name',
            'type': 'char',
            'required': True,
            'readonly': False
        }
    ]
}
```

#### **discover_modules(database_name: Optional[str] = None)**
Discovers installed Odoo modules.

**Parameters:**
- `database_name` (str, optional): Specific database to query

**Returns:** `Dict[str, Any]`
```python
{
    'success': True,
    'data': [
        {
            'name': 'base',
            'display_name': 'Base',
            'version': '16.0.1.0.0',
            'state': 'installed'
        }
    ]
}
```

#### **get_records(model_name: str, filters: Optional[Dict[str, Any]] = None, fields: Optional[List[str]] = None, limit: Optional[int] = None)**
Retrieves records from Odoo with filtering.

**Parameters:**
- `model_name` (str): Name of the Odoo model
- `filters` (List[Tuple], optional): Odoo domain filters
- `fields` (List[str], optional): Specific fields to retrieve
- `limit` (int, optional): Maximum number of records

**Returns:** `Dict[str, Any]`
```python
{
    'success': True,
    'data': [
        {
            'id': 1,
            'name': 'Company Name',
            'email': 'info@company.com'
        }
    ],
    'count': 1
}
```

#### **get_record(model_name: str, record_id: int, fields: Optional[List[str]] = None)**
Retrieves a single record from Odoo.

**Parameters:**
- `model_name` (str): Name of the Odoo model
- `record_id` (int): ID of the record
- `fields` (List[str], optional): Specific fields to retrieve

**Returns:** `Dict[str, Any]`
```python
{
    'success': True,
    'data': {
        'id': 1,
        'name': 'Company Name',
        'email': 'info@company.com',
        'is_company': True
    }
}
```

#### **create_record(model_name: str, record_data: Dict[str, Any])**
Creates a new record in Odoo.

**Parameters:**
- `model_name` (str): Name of the Odoo model
- `record_data` (Dict[str, Any]): Data for the new record

**Returns:** `Dict[str, Any]`
```python
{
    'success': True,
    'data': {
        'id': 123,
        'name': 'New Company'
    }
}
```

#### **update_record(model_name: str, record_id: int, record_data: Dict[str, Any])**
Updates an existing record in Odoo.

**Parameters:**
- `model_name` (str): Name of the Odoo model
- `record_id` (int): ID of the record to update
- `record_data` (Dict[str, Any]): Updated data

**Returns:** `Dict[str, Any]`
```python
{
    'success': True,
    'message': 'Record updated successfully'
}
```

#### **delete_record(model_name: str, record_id: int)**
Deletes a record from Odoo.

**Parameters:**
- `model_name` (str): Name of the Odoo model
- `record_id` (int): ID of the record to delete

**Returns:** `Dict[str, Any]`
```python
{
    'success': True,
    'message': 'Record deleted successfully'
}
```

#### **execute_method(model_name: str, method_name: str, record_ids: List[int], parameters: Optional[Dict[str, Any]] = None)**
Executes a method on Odoo records.

**Parameters:**
- `model_name` (str): Name of the Odoo model
- `method_name` (str): Name of the method to execute
- `record_ids` (List[int]): IDs of records to operate on
- `parameters` (Dict[str, Any], optional): Method parameters

**Returns:** `Dict[str, Any]`
```python
{
    'success': True,
    'data': 'Method executed successfully'
}
```

#### **get_database_info()**
Returns information about the Odoo database.

**Returns:** `Dict[str, Any]`
```python
{
    'success': True,
    'data': {
        'name': 'odoo_database',
        'version': '16.0',
        'language': 'en_US',
        'timezone': 'UTC'
    }
}
```

## VirtualFieldsInterface

Manages custom data extensions to Odoo models.

### **Constructor**

```python
VirtualFieldsInterface(solution_name: str)
```

### **Methods**

#### **set_custom_field(model_name: str, record_id: int, field_name: str, field_value: Any, field_type: str = 'char', database_name: Optional[str] = None)**
Sets a custom field value.

**Parameters:**
- `model_name` (str): Name of the Odoo model
- `record_id` (int): ID of the record
- `field_name` (str): Name of the custom field
- `field_value` (Any): Value to set
- `field_type` (str): Data type ('char', 'text', 'date', 'numeric', 'json')
- `database_name` (str, optional): Specific database

**Returns:** `Dict[str, Any]`
```python
{
    'success': True,
    'message': 'Custom field set successfully'
}
```

#### **get_custom_field(model_name: str, record_id: int, field_name: str, database_name: Optional[str] = None)**
Retrieves a custom field value.

**Parameters:**
- `model_name` (str): Name of the Odoo model
- `record_id` (int): ID of the record
- `field_name` (str): Name of the custom field
- `database_name` (str, optional): Specific database

**Returns:** `Dict[str, Any]`
```python
{
    'success': True,
    'data': 'field_value'
}
```

#### **get_custom_fields(model_name: str, record_id: int, database_name: Optional[str] = None)**
Retrieves all custom fields for a record.

**Parameters:**
- `model_name` (str): Name of the Odoo model
- `record_id` (int): ID of the record
- `database_name` (str, optional): Specific database

**Returns:** `Dict[str, Any]`
```python
{
    'success': True,
    'data': {
        'loyalty_tier': 'gold',
        'preferences': {'theme': 'dark'},
        'credit_limit': 50000.00
    }
}
```

#### **delete_custom_field(model_name: str, record_id: int, field_name: str, database_name: Optional[str] = None)**
Deletes a custom field.

**Parameters:**
- `model_name` (str): Name of the Odoo model
- `record_id` (int): ID of the record
- `field_name` (str): Name of the custom field
- `database_name` (str, optional): Specific database

**Returns:** `Dict[str, Any]`
```python
{
    'success': True,
    'message': 'Custom field deleted successfully'
}
```

#### **merge_odoo_with_custom(model_name: str, record_id: int, odoo_fields: Optional[List[str]] = None, database_name: Optional[str] = None)**
Merges Odoo data with custom fields.

**Parameters:**
- `model_name` (str): Name of the Odoo model
- `record_id` (int): ID of the record
- `odoo_fields` (List[str], optional): Specific Odoo fields to include
- `database_name` (str, optional): Specific database

**Returns:** `Dict[str, Any]`
```python
{
    'success': True,
    'data': {
        'odoo_data': {
            'id': 123,
            'name': 'Company Name',
            'email': 'info@company.com'
        },
        'custom_fields': {
            'loyalty_tier': 'gold',
            'preferences': {'theme': 'dark'}
        },
        'merged_data': {
            'id': 123,
            'name': 'Company Name',
            'email': 'info@company.com',
            'loyalty_tier': 'gold',
            'preferences': {'theme': 'dark'}
        }
    }
}
```

#### **get_virtual_model_schema(model_name: str, database_name: Optional[str] = None)**
Returns the virtual model schema including custom fields.

**Parameters:**
- `model_name` (str): Name of the Odoo model
- `database_name` (str, optional): Specific database

**Returns:** `Dict[str, Any]`
```python
{
    'success': True,
    'data': {
        'odoo_fields': [
            {'name': 'name', 'type': 'char', 'required': True},
            {'name': 'email', 'type': 'char', 'required': False}
        ],
        'custom_fields': [
            {'name': 'loyalty_tier', 'type': 'char', 'default': 'bronze'},
            {'name': 'preferences', 'type': 'json', 'default': {}}
        ]
    }
}
```

## MSMEInterface

Manages MSME-specific business operations.

### **Constructor**

```python
MSMEInterface(solution_name: str)
```

### **Methods**

#### **setup_business(business_type: str, config: Dict[str, Any])**
Sets up a new MSME business.

**Parameters:**
- `business_type` (str): Type of business ('retail', 'manufacturing', 'services')
- `config` (Dict[str, Any]): Business configuration

**Returns:** `Dict[str, Any]`
```python
{
    'success': True,
    'data': {
        'business_id': 123,
        'setup_complete': True,
        'next_steps': ['Configure KPIs', 'Set up workflows']
    }
}
```

#### **get_dashboard()**
Returns MSME dashboard data.

**Returns:** `Dict[str, Any]`
```python
{
    'success': True,
    'data': {
        'business_summary': {
            'total_revenue': 50000,
            'active_workflows': 5,
            'compliance_score': 85
        },
        'recent_activities': [...],
        'upcoming_tasks': [...]
    }
}
```

#### **calculate_kpis()**
Calculates MSME KPIs.

**Returns:** `Dict[str, Any]`
```python
{
    'success': True,
    'data': {
        'financial_kpis': {
            'revenue_growth': 15.5,
            'profit_margin': 25.3,
            'cash_flow': 'positive'
        },
        'operational_kpis': {
            'customer_satisfaction': 4.2,
            'process_efficiency': 78.5
        }
    }
}
```

#### **get_compliance_status()**
Returns compliance status.

**Returns:** `Dict[str, Any]`
```python
{
    'success': True,
    'data': {
        'overall_score': 85,
        'categories': {
            'financial': {'score': 90, 'status': 'compliant'},
            'operational': {'score': 80, 'status': 'warning'},
            'regulatory': {'score': 85, 'status': 'compliant'}
        }
    }
}
```

#### **update_business_profile(profile_data: Dict[str, Any])**
Updates business profile.

**Parameters:**
- `profile_data` (Dict[str, Any]): Updated profile information

**Returns:** `Dict[str, Any]`
```python
{
    'success': True,
    'message': 'Business profile updated successfully'
}
```

#### **get_marketing_data()**
Returns marketing data.

**Returns:** `Dict[str, Any]`
```python
{
    'success': True,
    'data': {
        'campaigns': [...],
        'customer_segments': [...],
        'marketing_metrics': {...}
    }
}
```

#### **get_analytics_summary()**
Returns analytics summary.

**Returns:** `Dict[str, Any]`
```python
{
    'success': True,
    'data': {
        'performance_metrics': {...},
        'trends': {...},
        'recommendations': [...]
    }
}
```

#### **create_custom_field(field_data: Dict[str, Any])**
Creates a custom field.

**Parameters:**
- `field_data` (Dict[str, Any]): Field configuration

**Returns:** `Dict[str, Any]`
```python
{
    'success': True,
    'data': {
        'field_id': 456,
        'field_name': 'custom_field'
    }
}
```

#### **get_business_templates()**
Returns available business templates.

**Returns:** `Dict[str, Any]`
```python
{
    'success': True,
    'data': [
        {
            'name': 'retail_standard',
            'display_name': 'Retail Standard',
            'description': 'Standard retail business setup',
            'features': ['inventory', 'sales', 'customer_management']
        }
    ]
}
```

#### **apply_business_template(template_name: str)**
Applies a business template.

**Parameters:**
- `template_name` (str): Name of the template to apply

**Returns:** `Dict[str, Any]`
```python
{
    'success': True,
    'message': 'Business template applied successfully',
    'data': {
        'applied_features': ['inventory', 'sales', 'customer_management']
    }
}
```

#### **get_setup_wizard_status()**
Returns setup wizard status.

**Returns:** `Dict[str, Any]`
```python
{
    'success': True,
    'data': {
        'current_step': 'configure_kpis',
        'completed_steps': ['business_info', 'industry_selection'],
        'total_steps': 5,
        'progress': 40
    }
}
```

#### **update_setup_wizard_step(step_name: str, step_data: Dict[str, Any])**
Updates setup wizard step.

**Parameters:**
- `step_name` (str): Name of the step
- `step_data` (Dict[str, Any]): Step data

**Returns:** `Dict[str, Any]`
```python
{
    'success': True,
    'message': 'Setup step updated successfully'
}
```

## BusinessIntelligenceInterface

Manages BI, analytics, and reporting.

### **Constructor**

```python
BusinessIntelligenceInterface(solution_name: str)
```

### **Methods**

#### **create_dashboard(dashboard_data: Dict[str, Any])**
Creates a new dashboard.

**Parameters:**
- `dashboard_data` (Dict[str, Any]): Dashboard configuration

**Returns:** `Dict[str, Any]`
```python
{
    'success': True,
    'data': {
        'dashboard_id': 123,
        'name': 'Sales Dashboard'
    }
}
```

#### **get_dashboards(dashboard_type: Optional[str] = None)**
Returns all dashboards or by type.

**Parameters:**
- `dashboard_type` (str, optional): Filter by dashboard type

**Returns:** `Dict[str, Any]`
```python
{
    'success': True,
    'data': [
        {
            'id': 123,
            'name': 'Sales Dashboard',
            'type': 'financial',
            'created_at': '2025-01-15T10:30:00Z'
        }
    ]
}
```

#### **update_dashboard(dashboard_id: int, dashboard_data: Dict[str, Any])**
Updates a dashboard.

**Parameters:**
- `dashboard_id` (int): ID of the dashboard
- `dashboard_data` (Dict[str, Any]): Updated dashboard data

**Returns:** `Dict[str, Any]`
```python
{
    'success': True,
    'message': 'Dashboard updated successfully'
}
```

#### **delete_dashboard(dashboard_id: int)**
Deletes a dashboard.

**Parameters:**
- `dashboard_id` (int): ID of the dashboard to delete

**Returns:** `Dict[str, Any]`
```python
{
    'success': True,
    'message': 'Dashboard deleted successfully'
}
```

#### **create_report(report_data: Dict[str, Any])**
Creates a new report.

**Parameters:**
- `report_data` (Dict[str, Any]): Report configuration

**Returns:** `Dict[str, Any]`
```python
{
    'success': True,
    'data': {
        'report_id': 456,
        'name': 'Monthly Sales Report'
    }
}
```

#### **get_reports(report_type: Optional[str] = None)**
Returns all reports or by type.

**Parameters:**
- `report_type` (str, optional): Filter by report type

**Returns:** `Dict[str, Any]`
```python
{
    'success': True,
    'data': [
        {
            'id': 456,
            'name': 'Monthly Sales Report',
            'type': 'financial',
            'schedule': 'monthly'
        }
    ]
}
```

#### **generate_report(report_id: int, parameters: Optional[Dict[str, Any]] = None)**
Generates a report with parameters.

**Parameters:**
- `report_id` (int): ID of the report
- `parameters` (Dict[str, Any], optional): Report parameters

**Returns:** `Dict[str, Any]`
```python
{
    'success': True,
    'data': {
        'report_url': '/reports/monthly_sales_2025_01.pdf',
        'generated_at': '2025-01-15T10:30:00Z'
    }
}
```

#### **create_kpi(kpi_data: Dict[str, Any])**
Creates a new KPI.

**Parameters:**
- `kpi_data` (Dict[str, Any]): KPI configuration

**Returns:** `Dict[str, Any]`
```python
{
    'success': True,
    'data': {
        'kpi_id': 789,
        'name': 'Monthly Revenue'
    }
}
```

#### **get_kpis(kpi_type: Optional[str] = None)**
Returns all KPIs or by type.

**Parameters:**
- `kpi_type` (str, optional): Filter by KPI type

**Returns:** `Dict[str, Any]`
```python
{
    'success': True,
    'data': [
        {
            'id': 789,
            'name': 'Monthly Revenue',
            'type': 'financial',
            'target_value': 50000
        }
    ]
}
```

#### **calculate_kpi(kpi_id: int)**
Calculates KPI value.

**Parameters:**
- `kpi_id` (int): ID of the KPI

**Returns:** `Dict[str, Any]`
```python
{
    'success': True,
    'data': {
        'current_value': 45000,
        'target_value': 50000,
        'percentage': 90.0,
        'status': 'on_track'
    }
}
```

#### **create_chart(chart_data: Dict[str, Any])**
Creates a new chart.

**Parameters:**
- `chart_data` (Dict[str, Any]): Chart configuration

**Returns:** `Dict[str, Any]`
```python
{
    'success': True,
    'data': {
        'chart_id': 101,
        'name': 'Revenue Trend'
    }
}
```

#### **get_charts(chart_type: Optional[str] = None)**
Returns all charts or by type.

**Parameters:**
- `chart_type` (str, optional): Filter by chart type

**Returns:** `Dict[str, Any]`
```python
{
    'success': True,
    'data': [
        {
            'id': 101,
            'name': 'Revenue Trend',
            'type': 'line',
            'data_source': 'sales_data'
        }
    ]
}
```

#### **get_analytics_data(data_source: str, filters: Optional[Dict[str, Any]] = None)**
Returns analytics data from various sources.

**Parameters:**
- `data_source` (str): Source of analytics data
- `filters` (Dict[str, Any], optional): Data filters

**Returns:** `Dict[str, Any]`
```python
{
    'success': True,
    'data': {
        'metrics': {...},
        'trends': {...},
        'insights': [...]
    }
}
```

## WorkflowInterface

Manages business workflows and approvals.

### **Constructor**

```python
WorkflowInterface(solution_name: str)
```

### **Methods**

#### **create_workflow_definition(workflow_data: Dict[str, Any])**
Creates a new workflow definition.

**Parameters:**
- `workflow_data` (Dict[str, Any]): Workflow configuration

**Returns:** `Dict[str, Any]`
```python
{
    'success': True,
    'data': {
        'workflow_id': 123,
        'name': 'Purchase Approval'
    }
}
```

#### **get_workflow_definitions(workflow_type: Optional[str] = None)**
Returns all workflow definitions or by type.

**Parameters:**
- `workflow_type` (str, optional): Filter by workflow type

**Returns:** `Dict[str, Any]`
```python
{
    'success': True,
    'data': [
        {
            'id': 123,
            'name': 'Purchase Approval',
            'type': 'approval',
            'steps_count': 3
        }
    ]
}
```

#### **start_workflow(workflow_definition_id: int, initial_data: Dict[str, Any])**
Starts a new workflow instance.

**Parameters:**
- `workflow_definition_id` (int): ID of the workflow definition
- `initial_data` (Dict[str, Any]): Initial workflow data

**Returns:** `Dict[str, Any]`
```python
{
    'success': True,
    'data': {
        'instance_id': 456,
        'workflow_name': 'Purchase Approval',
        'current_step': 'request'
    }
}
```

#### **get_active_workflows(user_id: Optional[int] = None)**
Returns active workflow instances.

**Parameters:**
- `user_id` (int, optional): Filter by user

**Returns:** `Dict[str, Any]`
```python
{
    'success': True,
    'data': [
        {
            'id': 456,
            'workflow_name': 'Purchase Approval',
            'current_step': 'manager_review',
            'started_at': '2025-01-15T10:30:00Z'
        }
    ]
}
```

#### **execute_workflow_step(workflow_instance_id: int, step_data: Dict[str, Any])**
Executes a workflow step.

**Parameters:**
- `workflow_instance_id` (int): ID of the workflow instance
- `step_data` (Dict[str, Any]): Step execution data

**Returns:** `Dict[str, Any]`
```python
{
    'success': True,
    'data': {
        'next_step': 'finance_approval',
        'step_completed': True,
        'workflow_status': 'in_progress'
    }
}
```

#### **create_approval_request(approval_data: Dict[str, Any])**
Creates an approval request.

**Parameters:**
- `approval_data` (Dict[str, Any]): Approval request data

**Returns:** `Dict[str, Any]`
```python
{
    'success': True,
    'data': {
        'request_id': 789,
        'status': 'pending'
    }
}
```

## AccountingInterface

Manages financial operations and accounting.

### **Constructor**

```python
AccountingInterface(solution_name: str)
```

### **Methods**

#### **create_cash_entry(entry_type: str, amount: float, description: str, category: str = '', date: Optional[str] = None)**
Creates a cash basis accounting entry.

**Parameters:**
- `entry_type` (str): Type of entry ('income' or 'expense')
- `amount` (float): Entry amount
- `description` (str): Entry description
- `category` (str, optional): Entry category
- `date` (str, optional): Entry date (ISO format)

**Returns:** `Dict[str, Any]`
```python
{
    'success': True,
    'data': {
        'entry_id': 123,
        'entry_type': 'income',
        'amount': 1500.00,
        'balance': 1500.00
    }
}
```

#### **get_basic_ledger(start_date: Optional[str] = None, end_date: Optional[str] = None, account_type: Optional[str] = None)**
Returns simple general ledger.

**Parameters:**
- `start_date` (str, optional): Start date (ISO format)
- `end_date` (str, optional): End date (ISO format)
- `account_type` (str, optional): Account type filter

**Returns:** `Dict[str, Any]`
```python
{
    'success': True,
    'data': {
        'entries': [...],
        'summary': {
            'total_income': 5000.00,
            'total_expenses': 3000.00,
            'net_income': 2000.00
        }
    }
}
```

#### **track_income_expense(transaction_type: str, amount: float, description: str, category: str = '', date: Optional[str] = None)**
Tracks simple income and expense.

**Parameters:**
- `transaction_type` (str): Type of transaction ('income' or 'expense')
- `amount` (float): Transaction amount
- `description` (str): Transaction description
- `category` (str, optional): Transaction category
- `date` (str, optional): Transaction date (ISO format)

**Returns:** `Dict[str, Any]`
```python
{
    'success': True,
    'data': {
        'transaction_id': 456,
        'type': 'income',
        'amount': 2500.00
    }
}
```

#### **get_income_expense_summary(period: str = 'month')**
Returns income and expense summary.

**Parameters:**
- `period` (str): Summary period ('day', 'week', 'month', 'year')

**Returns:** `Dict[str, Any]`
```python
{
    'success': True,
    'data': {
        'period': 'month',
        'income': 5000.00,
        'expenses': 3000.00,
        'net_income': 2000.00,
        'trend': 'increasing'
    }
}
```

#### **get_financial_health_indicators()**
Returns basic financial health indicators.

**Returns:** `Dict[str, Any]`
```python
{
    'success': True,
    'data': {
        'cash_flow': 'positive',
        'profit_margin': 25.5,
        'debt_ratio': 0.3,
        'liquidity_ratio': 2.1
    }
}
```

#### **calculate_tax(amount: float, tax_type: str = 'vat', tax_rate: Optional[float] = None)**
Calculates tax amounts.

**Parameters:**
- `amount` (float): Base amount
- `tax_type` (str): Type of tax
- `tax_rate` (float, optional): Tax rate (if not provided, uses default)

**Returns:** `Dict[str, Any]`
```python
{
    'success': True,
    'data': {
        'base_amount': 1000.00,
        'tax_rate': 0.15,
        'tax_amount': 150.00,
        'total_amount': 1150.00
    }
}
```

#### **get_cash_position(date: Optional[str] = None)**
Returns current cash position.

**Parameters:**
- `date` (str, optional): Specific date (ISO format)

**Returns:** `Dict[str, Any]`
```python
{
    'success': True,
    'data': {
        'cash_balance': 5000.00,
        'as_of_date': '2025-01-15',
        'change_from_previous': 500.00
    }
}
```

#### **create_recurring_transaction(transaction_data: Dict[str, Any])**
Creates a recurring transaction.

**Parameters:**
- `transaction_data` (Dict[str, Any]): Recurring transaction configuration

**Returns:** `Dict[str, Any]**
```python
{
    'success': True,
    'data': {
        'recurring_id': 789,
        'next_execution': '2025-02-01'
    }
}
```

#### **get_recurring_transactions(status: Optional[str] = None)**
Returns recurring transactions.

**Parameters:**
- `status` (str, optional): Filter by status ('active', 'paused', 'completed')

**Returns:** `Dict[str, Any]**
```python
{
    'success': True,
    'data': [
        {
            'id': 789,
            'description': 'Monthly Rent',
            'amount': 500.00,
            'frequency': 'monthly',
            'status': 'active'
        }
    ]
}
```

## CacheInterface

Manages solution-specific caching.

### **Constructor**

```python
CacheInterface(solution_name: str)
```

### **Methods**

#### **get_cache(key: str, database_name: Optional[str] = None)**
Retrieves a cached value.

**Parameters:**
- `key` (str): Cache key
- `database_name` (str, optional): Specific database

**Returns:** `Dict[str, Any]**
```python
{
    'success': True,
    'data': 'cached_value',
    'expires_at': '2025-01-15T11:30:00Z'
}
```

#### **set_cache(key: str, value: Any, expiry_hours: int = 24, database_name: Optional[str] = None)**
Sets a cache value.

**Parameters:**
- `key` (str): Cache key
- `value` (Any): Value to cache
- `expiry_hours` (int): Expiry time in hours
- `database_name` (str, optional): Specific database

**Returns:** `Dict[str, Any]**
```python
{
    'success': True,
    'message': 'Value cached successfully'
}
```

#### **delete_cache(key: str, database_name: Optional[str] = None)**
Deletes a cache entry.

**Parameters:**
- `key` (str): Cache key to delete
- `database_name` (str, optional): Specific database

**Returns:** `Dict[str, Any]**
```python
{
    'success': True,
    'message': 'Cache entry deleted successfully'
}
```

#### **clear_cache(database_name: Optional[str] = None)**
Clears all cache for a database.

**Parameters:**
- `database_name` (str, optional): Specific database

**Returns:** `Dict[str, Any]**
```python
{
    'success': True,
    'message': 'Cache cleared successfully'
}
```

#### **get_cache_stats(database_name: Optional[str] = None)**
Returns cache statistics.

**Parameters:**
- `database_name` (str, optional): Specific database

**Returns:** `Dict[str, Any]**
```python
{
    'success': True,
    'data': {
        'total_entries': 150,
        'total_size_mb': 25.5,
        'hit_rate': 0.85,
        'expired_entries': 10
    }
}
```

## Response Format

All FBS service methods return responses in a consistent format:

### **Success Response**

```python
{
    'success': True,
    'data': {...},  # Response data
    'message': 'Operation completed successfully',  # Optional
    'timestamp': '2025-01-15T10:30:00Z'  # Optional
}
```

### **Error Response**

```python
{
    'success': False,
    'error': 'Error description',
    'error_code': 'ERROR_CODE',  # Optional
    'timestamp': '2025-01-15T10:30:00Z'
}
```

### **Response Fields**

- **`success`** (bool): Whether the operation was successful
- **`data`** (Any): Response data (only present on success)
- **`message`** (str, optional): Success message
- **`error`** (str, optional): Error description (only present on failure)
- **`error_code`** (str, optional): Machine-readable error code
- **`timestamp`** (str, optional): ISO timestamp of the response

## Error Codes

Common error codes returned by FBS services:

- **`VALIDATION_ERROR`**: Input validation failed
- **`NOT_FOUND`**: Requested resource not found
- **`PERMISSION_DENIED`**: Insufficient permissions
- **`ODOO_CONNECTION_ERROR`**: Odoo connection failed
- **`DATABASE_ERROR`**: Database operation failed
- **`LICENSE_LIMIT_EXCEEDED`**: License limit reached
- **`FEATURE_DISABLED`**: Feature not enabled in current plan

## Rate Limiting

FBS services implement rate limiting to ensure system stability:

- **Standard operations**: 1000 requests per minute
- **Heavy operations**: 100 requests per minute
- **Bulk operations**: 50 requests per minute

Rate limit headers are included in responses:
- `X-RateLimit-Limit`: Request limit per window
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: Time when the rate limit resets

## Next Steps

1. **Read the [Developer Guide](DEVELOPER_GUIDE.md)** - Deep dive into development patterns
2. **Check [Odoo Integration](ODOO_INTEGRATION.md)** - Master Odoo + Virtual Fields
3. **Review [Integration Guide](INTEGRATION.md)** - Learn embedding patterns
4. **Start building** - Begin implementing FBS in your projects

---

**API Reference Complete!** 📚

You now have comprehensive documentation of all FBS service interfaces. Use this reference to build powerful business applications with Odoo integration and FBS Virtual Fields technology.
