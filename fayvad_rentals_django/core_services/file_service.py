"""
Simple File Attachment Service
Replaces complex document management with basic file attachments
"""

from django.db import models
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from typing import Dict, Any, Optional
from django.contrib.auth import get_user_model
import os

User = get_user_model()


class SimpleFileAttachment(models.Model):
    """
    Simple file attachment model
    Basic file storage for maintenance, payments, etc.
    """

    # Related object
    content_type = models.CharField(max_length=100)  # e.g., 'maintenance', 'payment'
    object_id = models.PositiveIntegerField()
    content_object = None  # Generic relation would be overkill

    # File info
    file = models.FileField(upload_to='attachments/%Y/%m/')
    filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField()
    mime_type = models.CharField(max_length=100, blank=True)

    # Metadata
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]

    def __str__(self):
        return f"{self.filename} ({self.content_type})"

    @staticmethod
    def attach_file(content_type: str, object_id: int, uploaded_file, user: User = None, description: str = "") -> Dict[str, Any]:
        """
        Attach a file to an object
        """
        try:
            # Save the file
            file_name = uploaded_file.name
            file_path = f"attachments/{content_type}/{object_id}/{file_name}"

            # Save to storage
            path = default_storage.save(file_path, ContentFile(uploaded_file.read()))

            # Create attachment record
            attachment = SimpleFileAttachment.objects.create(
                content_type=content_type,
                object_id=object_id,
                file=path,
                filename=file_name,
                file_size=uploaded_file.size,
                mime_type=uploaded_file.content_type or '',
                uploaded_by=user,
                description=description
            )

            return {
                'success': True,
                'attachment_id': attachment.id,
                'file_url': attachment.file.url,
                'filename': attachment.filename
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def get_attachments(content_type: str, object_id: int) -> list:
        """
        Get all attachments for an object
        """
        return list(
            SimpleFileAttachment.objects.filter(
                content_type=content_type,
                object_id=object_id
            ).values(
                'id', 'filename', 'file_size', 'mime_type',
                'uploaded_at', 'description', 'file'
            )
        )

    @staticmethod
    def delete_attachment(attachment_id: int, user: User = None) -> Dict[str, Any]:
        """
        Delete a file attachment
        """
        try:
            attachment = SimpleFileAttachment.objects.get(id=attachment_id)

            # Delete file from storage
            if attachment.file:
                attachment.file.delete(save=False)

            # Delete record
            attachment.delete()

            return {'success': True}

        except SimpleFileAttachment.DoesNotExist:
            return {'success': False, 'error': 'Attachment not found'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

