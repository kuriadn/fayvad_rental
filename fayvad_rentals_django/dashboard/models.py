"""
Dashboard and analytics models
KPIs, metrics, and dashboard configurations
"""

from django.db import models
import uuid

class DashboardType(models.TextChoices):
    """Dashboard type choices"""
    OVERVIEW = "overview", "Overview"
    FINANCIAL = "financial", "Financial"
    OCCUPANCY = "occupancy", "Occupancy"
    MAINTENANCE = "maintenance", "Maintenance"
    TENANT = "tenant", "Tenant"
    PROPERTY = "property", "Property"


class MetricType(models.TextChoices):
    """Metric type choices"""
    COUNT = "count", "Count"
    SUM = "sum", "Sum"
    AVERAGE = "average", "Average"
    PERCENTAGE = "percentage", "Percentage"
    TREND = "trend", "Trend"


class Dashboard(models.Model):
    """
    Dashboard configuration model
    """

    # Primary key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Dashboard information
    name = models.CharField(max_length=200, help_text="Dashboard name")
    dashboard_type = models.CharField(
        max_length=20,
        choices=DashboardType.choices,
        default=DashboardType.OVERVIEW,
        help_text="Type of dashboard"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Dashboard description"
    )

    # Configuration
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this dashboard is active"
    )
    is_default = models.BooleanField(
        default=False,
        help_text="Whether this is the default dashboard"
    )
    config = models.JSONField(
        default=dict,
        blank=True,
        help_text="Dashboard configuration (widgets, layout, etc.)"
    )

    # Metadata
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='created_dashboards',
        help_text="User who created the dashboard"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['dashboard_type']),
            models.Index(fields=['is_active']),
            models.Index(fields=['is_default']),
            models.Index(fields=['created_by']),
        ]

    def __str__(self):
        return f"{self.name} ({self.dashboard_type})"


class KPI(models.Model):
    """
    Key Performance Indicator model
    """

    # Primary key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # KPI information
    name = models.CharField(max_length=200, help_text="KPI name")
    code = models.CharField(
        max_length=100,
        unique=True,
        help_text="Unique KPI code for identification"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="KPI description"
    )

    # Metric configuration
    metric_type = models.CharField(
        max_length=20,
        choices=MetricType.choices,
        default=MetricType.COUNT,
        help_text="Type of metric calculation"
    )
    model_name = models.CharField(
        max_length=100,
        help_text="Django model name (e.g., 'tenants.Tenant')"
    )
    field_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Field name for aggregation (optional)"
    )
    filters = models.JSONField(
        default=dict,
        blank=True,
        help_text="Filters to apply to the query"
    )

    # Display
    unit = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Unit of measurement (e.g., 'KES', '%', 'count')"
    )
    format_string = models.CharField(
        max_length=100,
        default="{value}",
        help_text="Format string for displaying the value"
    )

    # Target and thresholds
    target_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Target value for this KPI"
    )
    warning_threshold = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Warning threshold value"
    )
    critical_threshold = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Critical threshold value"
    )

    # Status
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this KPI is active"
    )

    # Metadata
    category = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="KPI category for grouping"
    )
    dashboard_types = models.JSONField(
        default=list,
        blank=True,
        help_text="Dashboard types where this KPI should appear"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['metric_type']),
            models.Index(fields=['is_active']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"

    def calculate_value(self):
        """Calculate the KPI value"""
        try:
            # Import the model dynamically
            app_label, model_name = self.model_name.split('.')
            from django.apps import apps
            model = apps.get_model(app_label, model_name)

            # Build the query
            queryset = model.objects.all()

            # Apply filters
            for field, value in self.filters.items():
                if isinstance(value, dict):
                    # Handle complex filters like __gte, __lte, etc.
                    for lookup, val in value.items():
                        filter_key = f"{field}__{lookup}"
                        queryset = queryset.filter(**{filter_key: val})
                else:
                    queryset = queryset.filter(**{field: value})

            # Calculate based on metric type
            if self.metric_type == MetricType.COUNT:
                value = queryset.count()
            elif self.metric_type == MetricType.SUM and self.field_name:
                result = queryset.aggregate(sum_value=models.Sum(self.field_name))
                value = result['sum_value'] or 0
            elif self.metric_type == MetricType.AVERAGE and self.field_name:
                result = queryset.aggregate(avg_value=models.Avg(self.field_name))
                value = result['avg_value'] or 0
            elif self.metric_type == MetricType.PERCENTAGE:
                # For percentages, we might need custom logic
                # This is a placeholder for percentage calculations
                value = 0
            else:
                value = 0

            return float(value) if value is not None else 0

        except Exception as e:
            # Log error and return 0
            print(f"Error calculating KPI {self.code}: {e}")
            return 0

    @property
    def status(self):
        """Get KPI status based on thresholds"""
        if not self.is_active:
            return "inactive"

        value = self.calculate_value()

        if self.critical_threshold is not None and value <= self.critical_threshold:
            return "critical"
        elif self.warning_threshold is not None and value <= self.warning_threshold:
            return "warning"
        else:
            return "normal"

    def get_formatted_value(self):
        """Get formatted KPI value"""
        value = self.calculate_value()
        try:
            return self.format_string.format(value=value)
        except:
            return str(value)
