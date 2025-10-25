"""
Document management models
File storage and document tracking
"""

from django.db import models
from django.core.validators import FileExtensionValidator
import uuid

class DocumentType(models.TextChoices):
    """Document type choices"""
    CONTRACT = "contract", "Contract"
    AGREEMENT = "agreement", "Agreement"
    ID_DOCUMENT = "id_document", "ID Document"
    RECEIPT = "receipt", "Receipt"
    INVOICE = "invoice", "Invoice"
    OTHER = "other", "Other"


class DocumentStatus(models.TextChoices):
    """Document status choices"""
    DRAFT = "draft", "Draft"
    ACTIVE = "active", "Active"
    ARCHIVED = "archived", "Archived"


class Document(models.Model):
    """
    Document model for file and document management
    """

    # Primary key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Document information
    title = models.CharField(
        max_length=200,
        help_text="Document title or name"
    )
    document_type = models.CharField(
        max_length=20,
        choices=DocumentType.choices,
        help_text="Type of document"
    )

    # File information
    file = models.FileField(
        upload_to='documents/%Y/%m/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator([
            'pdf', 'doc', 'docx', 'txt', 'jpg', 'jpeg', 'png', 'gif'
        ])],
        help_text="Uploaded document file"
    )
    filename = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Original filename"
    )
    file_size = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="File size in bytes"
    )
    mime_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="MIME type of the file"
    )

    # Related entities
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='documents',
        help_text="Associated tenant"
    )
    rental_agreement = models.ForeignKey(
        'rentals.RentalAgreement',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='documents',
        help_text="Associated rental agreement"
    )
    room = models.ForeignKey(
        'properties.Room',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='documents',
        help_text="Associated room"
    )

    # Status and metadata
    status = models.CharField(
        max_length=20,
        choices=DocumentStatus.choices,
        default=DocumentStatus.DRAFT,
        help_text="Document status"
    )

    # Requirements and references
    is_required = models.BooleanField(
        default=False,
        help_text="Whether this document is required"
    )
    reference_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times this document is referenced"
    )

    # Content and organization
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Document description or notes"
    )
    tags = models.JSONField(
        default=list,
        blank=True,
        help_text="Tags for document categorization"
    )
    version = models.CharField(
        max_length=20,
        default="1.0",
        help_text="Document version"
    )

    # Access control
    is_public = models.BooleanField(
        default=False,
        help_text="Whether document is publicly accessible"
    )
    access_permissions = models.JSONField(
        default=dict,
        blank=True,
        help_text="Access permissions for the document"
    )

    # Audit
    uploaded_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='uploaded_documents',
        help_text="User who uploaded the document"
    )
    reviewed_by = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Person who reviewed the document"
    )
    reviewed_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date when document was reviewed"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['document_type']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['tenant']),
            models.Index(fields=['rental_agreement']),
            models.Index(fields=['room']),
            models.Index(fields=['uploaded_by']),
        ]

    def __str__(self):
        return f"{self.title} ({self.document_type})"

    @property
    def is_active(self) -> bool:
        """Check if document is active"""
        return self.status == DocumentStatus.ACTIVE

    @property
    def is_archived(self) -> bool:
        """Check if document is archived"""
        return self.status == DocumentStatus.ARCHIVED

    @property
    def file_extension(self) -> str:
        """Get file extension"""
        if not self.filename:
            return ""
        return self.filename.split('.')[-1].lower() if '.' in self.filename else ""

    @property
    def tags_list(self) -> list:
        """Get tags as list"""
        return self.tags if isinstance(self.tags, list) else []

    @property
    def is_image(self) -> bool:
        """Check if document is an image"""
        return self.file_extension in ['jpg', 'jpeg', 'png', 'gif']

    @property
    def is_pdf(self) -> bool:
        """Check if document is a PDF"""
        return self.file_extension == 'pdf'

    @property
    def size_mb(self) -> float:
        """Get file size in MB"""
        if not self.file_size:
            return 0.0
        return self.file_size / (1024 * 1024)

    @property
    def file_url(self) -> str:
        """Get file URL"""
        if self.file:
            return self.file.url
        return ""

    def activate_document(self):
        """Mark document as active"""
        self.status = DocumentStatus.ACTIVE
        self.save()

    def archive_document(self):
        """Archive document"""
        self.status = DocumentStatus.ARCHIVED
        self.save()

    def increment_reference_count(self):
        """Increment reference count"""
        self.reference_count += 1
        self.save()

    def add_tag(self, tag: str):
        """Add tag to document"""
        if tag not in self.tags_list:
            self.tags.append(tag)
            self.save()

    def remove_tag(self, tag: str):
        """Remove tag from document"""
        if tag in self.tags_list:
            self.tags.remove(tag)
            self.save()

    def clean(self):
        """Validate model data"""
        if not self.title or not self.title.strip():
            raise ValueError("Title cannot be empty")

        if self.file_size and (self.file_size <= 0 or self.file_size > 10 * 1024 * 1024):
            raise ValueError("File size must be between 1 byte and 10MB")

    def save(self, *args, **kwargs):
        """Override save to handle file metadata"""
        if self.file and not self.filename:
            self.filename = self.file.name

        if self.file and not self.file_size:
            self.file_size = self.file.size

        if self.file and not self.mime_type:
            # Get MIME type from file
            import mimetypes
            self.mime_type = mimetypes.guess_type(self.filename)[0]

        super().save(*args, **kwargs)
