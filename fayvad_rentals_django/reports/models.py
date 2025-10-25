"""
Report generation models
Report templates, configurations, and generated reports
"""

from django.db import models
import uuid

class ReportType(models.TextChoices):
    """Report type choices"""
    FINANCIAL = "financial", "Financial Report"
    OCCUPANCY = "occupancy", "Occupancy Report"
    MAINTENANCE = "maintenance", "Maintenance Report"
    TENANT = "tenant", "Tenant Report"
    REVENUE = "revenue", "Revenue Report"
    COLLECTION = "collection", "Collection Report"
    PROPERTY = "property", "Property Report"


class ExportFormat(models.TextChoices):
    """Export format choices"""
    JSON = "json", "JSON"
    CSV = "csv", "CSV"
    PDF = "pdf", "PDF"
    EXCEL = "excel", "Excel"


class ReportTemplate(models.Model):
    """
    Report template configuration model
    """

    # Primary key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Template information
    name = models.CharField(max_length=200, help_text="Report template name")
    report_type = models.CharField(
        max_length=20,
        choices=ReportType.choices,
        help_text="Type of report this template generates"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Template description"
    )

    # Configuration
    config = models.JSONField(
        default=dict,
        blank=True,
        help_text="Template configuration (filters, fields, formatting)"
    )
    default_filters = models.JSONField(
        default=dict,
        blank=True,
        help_text="Default filter values for this template"
    )
    available_formats = models.JSONField(
        default=list,
        blank=True,
        help_text="Available export formats for this template"
    )

    # Status
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this template is active"
    )
    is_default = models.BooleanField(
        default=False,
        help_text="Whether this is the default template for its type"
    )

    # Metadata
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='created_report_templates',
        help_text="User who created the template"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['report_type', 'name']
        indexes = [
            models.Index(fields=['report_type']),
            models.Index(fields=['is_active']),
            models.Index(fields=['is_default']),
            models.Index(fields=['created_by']),
        ]

    def __str__(self):
        return f"{self.name} ({self.report_type})"


class GeneratedReport(models.Model):
    """
    Generated report storage model
    """

    # Primary key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Report information
    title = models.CharField(max_length=200, help_text="Report title")
    report_type = models.CharField(
        max_length=20,
        choices=ReportType.choices,
        help_text="Type of report"
    )

    # Generation details
    filters_used = models.JSONField(
        default=dict,
        blank=True,
        help_text="Filters used to generate this report"
    )
    export_format = models.CharField(
        max_length=20,
        choices=ExportFormat.choices,
        default=ExportFormat.JSON,
        help_text="Format of the exported report"
    )

    # File storage (if applicable)
    file = models.FileField(
        upload_to='reports/%Y/%m/',
        null=True,
        blank=True,
        help_text="Generated report file"
    )
    file_size = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="File size in bytes"
    )

    # Report data (for JSON storage)
    report_data = models.JSONField(
        null=True,
        blank=True,
        help_text="JSON representation of report data"
    )

    # Status
    is_complete = models.BooleanField(
        default=False,
        help_text="Whether report generation is complete"
    )
    error_message = models.TextField(
        blank=True,
        null=True,
        help_text="Error message if generation failed"
    )

    # Metadata
    generated_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='generated_reports',
        help_text="User who generated the report"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this report expires and can be deleted"
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['report_type']),
            models.Index(fields=['export_format']),
            models.Index(fields=['is_complete']),
            models.Index(fields=['generated_by']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"{self.title} ({self.report_type} - {self.export_format})"

    @property
    def is_expired(self):
        """Check if report has expired"""
        if not self.expires_at:
            return False
        from django.utils import timezone
        return timezone.now() > self.expires_at

    @property
    def download_url(self):
        """Get download URL for the report file"""
        if self.file:
            return self.file.url
        return None
