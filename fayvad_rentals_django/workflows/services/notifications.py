"""
Notification Service
Handles workflow notifications and escalations
"""

from typing import Dict, List, Any, Optional
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class WorkflowNotification(models.Model):
    """
    Model for storing workflow notifications
    """

    NOTIFICATION_TYPES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('in_app', 'In-App'),
        ('push', 'Push Notification'),
    ]

    PRIORITIES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workflow_notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    priority = models.CharField(max_length=20, choices=PRIORITIES, default='medium')

    title = models.CharField(max_length=200)
    message = models.TextField()

    # Related workflow instance
    instance_type = models.CharField(max_length=100)  # Model class name
    instance_id = models.CharField(max_length=50)     # Instance UUID

    # Event that triggered notification
    event_type = models.CharField(max_length=100)
    event_data = models.JSONField(default=dict)

    # Status
    sent_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    is_sent = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)

    # Escalation
    escalation_level = models.PositiveIntegerField(default=0)
    next_escalation = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['instance_type', 'instance_id']),
            models.Index(fields=['is_sent', 'sent_at']),
            models.Index(fields=['next_escalation']),
        ]

    def __str__(self):
        return f"{self.notification_type} to {self.recipient}: {self.title}"

    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()

    def mark_as_sent(self):
        """Mark notification as sent"""
        if not self.is_sent:
            self.is_sent = True
            self.sent_at = timezone.now()
            self.save()


class NotificationService:
    """
    Service for managing workflow notifications
    """

    # Notification templates by event type
    NOTIFICATION_TEMPLATES = {
        'maintenance_assigned': {
            'title': 'Maintenance Request Assigned',
            'template': 'workflows/notifications/maintenance_assigned.html',
            'email_subject': 'Maintenance Request #{request_number} Assigned',
        },
        'maintenance_completed': {
            'title': 'Maintenance Request Completed',
            'template': 'workflows/notifications/maintenance_completed.html',
            'email_subject': 'Maintenance Request #{request_number} Completed',
        },
        'payment_verified': {
            'title': 'Payment Verified',
            'template': 'workflows/notifications/payment_verified.html',
            'email_subject': 'Payment #{payment_number} Verified',
        },
        'payment_rejected': {
            'title': 'Payment Rejected',
            'template': 'workflows/notifications/payment_rejected.html',
            'email_subject': 'Payment #{payment_number} Rejected',
        },
        'escalation': {
            'title': 'Urgent Attention Required',
            'template': 'workflows/notifications/escalation.html',
            'email_subject': 'URGENT: Action Required - {title}',
        },
    }

    @staticmethod
    def notify_workflow_transition(instance: models.Model,
                                 event: str,
                                 user,
                                 **kwargs) -> List[WorkflowNotification]:
        """
        Send notifications for workflow transition
        """
        notifications = []

        try:
            # Get notification configuration for this event
            config = NotificationService._get_notification_config(event, instance)
            if not config:
                return notifications

            # Determine recipients
            recipients = NotificationService._get_recipients_for_event(event, instance, user)

            for recipient in recipients:
                notification = NotificationService._create_notification(
                    recipient=recipient,
                    instance=instance,
                    event=event,
                    config=config,
                    event_data=kwargs
                )

                if notification:
                    notifications.append(notification)

                    # Send immediate notifications
                    NotificationService._send_notification(notification, config)

        except Exception as e:
            logger.error(f"Failed to send workflow notifications: {e}")

        return notifications

    @staticmethod
    def _get_notification_config(event: str, instance: models.Model) -> Optional[Dict[str, Any]]:
        """Get notification configuration for event"""
        # Default configurations
        configs = {
            'assign_technician': {
                'title': 'Maintenance Request Assigned',
                'template': 'maintenance_assigned',
                'priority': 'medium',
                'notify_tenant': True,
                'notify_staff': True,
            },
            'complete_request': {
                'title': 'Maintenance Request Completed',
                'template': 'maintenance_completed',
                'priority': 'medium',
                'notify_tenant': True,
                'notify_staff': False,
            },
            'verify_payment': {
                'title': 'Payment Verified',
                'template': 'payment_verified',
                'priority': 'medium',
                'notify_tenant': True,
                'notify_staff': False,
            },
            'reject_payment': {
                'title': 'Payment Rejected',
                'template': 'payment_rejected',
                'priority': 'high',
                'notify_tenant': True,
                'notify_staff': False,
            },
        }

        return configs.get(event)

    @staticmethod
    def _get_recipients_for_event(event: str, instance: models.Model, user) -> List[User]:
        """Determine who should receive notifications for this event"""
        recipients = []

        config = NotificationService._get_notification_config(event, instance)

        if hasattr(instance, 'tenant') and config.get('notify_tenant'):
            # Notify tenant
            if hasattr(instance.tenant, 'user'):
                recipients.append(instance.tenant.user)

        if config.get('notify_staff'):
            # Notify relevant staff
            from django.contrib.auth.models import Group

            # Get maintenance staff group
            try:
                maintenance_group = Group.objects.get(name='Maintenance Staff')
                recipients.extend(list(maintenance_group.user_set.all()))
            except Group.DoesNotExist:
                # Fallback: notify all staff
                recipients.extend(list(User.objects.filter(is_staff=True)))

        # Always notify the user who triggered the event (for audit)
        if user not in recipients:
            recipients.append(user)

        return list(set(recipients))  # Remove duplicates

    @staticmethod
    def _create_notification(recipient: User,
                           instance: models.Model,
                           event: str,
                           config: Dict[str, Any],
                           event_data: Dict[str, Any]) -> WorkflowNotification:
        """Create notification record"""
        try:
            # Generate message content
            context = {
                'recipient': recipient,
                'instance': instance,
                'event': event,
                'event_data': event_data,
                'config': config,
            }

            title = config['title']
            message = NotificationService._render_notification_message(config, context)

            # Convert non-serializable objects in event_data
            import json
            from decimal import Decimal

            def make_serializable(obj):
                if isinstance(obj, Decimal):
                    return float(obj)
                elif hasattr(obj, '__dict__'):
                    # For model instances, just store the string representation
                    return str(obj)
                else:
                    return obj

            # Make event_data JSON serializable
            serializable_event_data = {}
            for key, value in event_data.items():
                try:
                    # Test if it's JSON serializable
                    json.dumps(value)
                    serializable_event_data[key] = value
                except (TypeError, ValueError):
                    # If not serializable, convert it
                    serializable_event_data[key] = make_serializable(value)

            notification = WorkflowNotification.objects.create(
                recipient=recipient,
                notification_type='in_app',  # Default to in-app
                priority=config.get('priority', 'medium'),
                title=title,
                message=message,
                instance_type=instance.__class__.__name__,
                instance_id=str(instance.id),
                event_type=event,
                event_data=serializable_event_data,
            )

            return notification

        except Exception as e:
            logger.error(f"Failed to create notification: {e}")
            return None

    @staticmethod
    def _render_notification_message(config: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Render notification message from template"""
        try:
            template_name = config.get('template')
            if template_name and template_name in NotificationService.NOTIFICATION_TEMPLATES:
                template_config = NotificationService.NOTIFICATION_TEMPLATES[template_name]
                # For now, return a simple message
                # In production, this would render the actual template
                instance = context['instance']
                event = context['event']

                if 'maintenance' in template_name:
                    return f"Maintenance request {getattr(instance, 'request_number', instance.id)} has been {event.replace('_', ' ')}."
                elif 'payment' in template_name:
                    return f"Payment {getattr(instance, 'payment_number', instance.id)} has been {event.replace('_', ' ')}."

            # Fallback message
            return f"Workflow event: {context['event']} for {context['instance'].__class__.__name__}"

        except Exception as e:
            logger.error(f"Failed to render notification message: {e}")
            return f"Workflow event: {context['event']}"

    @staticmethod
    def _send_notification(notification: WorkflowNotification, config: Dict[str, Any]):
        """Send notification via appropriate channel"""
        try:
            if notification.notification_type == 'email':
                NotificationService._send_email_notification(notification, config)
            elif notification.notification_type == 'sms':
                NotificationService._send_sms_notification(notification, config)
            # Mark as sent for in-app notifications
            elif notification.notification_type == 'in_app':
                notification.mark_as_sent()

        except Exception as e:
            logger.error(f"Failed to send notification {notification.id}: {e}")

    @staticmethod
    def _send_email_notification(notification: WorkflowNotification, config: Dict[str, Any]):
        """Send email notification"""
        try:
            subject = config.get('email_subject', notification.title)
            recipient_email = notification.recipient.email

            if recipient_email:
                send_mail(
                    subject=subject,
                    message=notification.message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[recipient_email],
                    fail_silently=True,
                )

                notification.mark_as_sent()
                logger.info(f"Email notification sent to {recipient_email}")

        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")

    @staticmethod
    def _send_sms_notification(notification: WorkflowNotification, config: Dict[str, Any]):
        """Send SMS notification"""
        # Placeholder for SMS integration
        # Would integrate with services like Twilio, Africa's Talking, etc.
        logger.info(f"SMS notification would be sent to {notification.recipient.phone}")
        notification.mark_as_sent()

    @staticmethod
    def schedule_escalation(instance: models.Model,
                          event_type: str,
                          escalation_hours: int = 24,
                          priority: str = 'high'):
        """
        Schedule escalation notification for overdue items
        """
        try:
            escalation_time = timezone.now() + timezone.timedelta(hours=escalation_hours)

            # Find staff to notify
            from django.contrib.auth.models import Group

            try:
                staff_group = Group.objects.get(name='Property Managers')
                recipients = list(staff_group.user_set.all())
            except Group.DoesNotExist:
                recipients = list(User.objects.filter(is_staff=True, is_superuser=True))

            notifications = []
            for recipient in recipients:
                notification = WorkflowNotification.objects.create(
                    recipient=recipient,
                    notification_type='in_app',
                    priority=priority,
                    title=f'ESCALATION: {event_type.replace("_", " ").title()}',
                    message=f'Urgent attention required for {instance.__class__.__name__} {instance.id}',
                    instance_type=instance.__class__.__name__,
                    instance_id=str(instance.id),
                    event_type='escalation',
                    event_data={'original_event': event_type, 'escalation_hours': escalation_hours},
                    escalation_level=1,
                    next_escalation=escalation_time,
                )
                notifications.append(notification)

            logger.info(f"Escalation scheduled for {instance.__class__.__name__} {instance.id}")
            return notifications

        except Exception as e:
            logger.error(f"Failed to schedule escalation: {e}")
            return []

    @staticmethod
    def get_user_notifications(user, unread_only: bool = False) -> List[Dict[str, Any]]:
        """Get notifications for a user"""
        try:
            queryset = WorkflowNotification.objects.filter(recipient=user)

            if unread_only:
                queryset = queryset.filter(is_read=False)

            notifications = queryset.order_by('-created_at')[:20]

            return [{
                'id': str(n.id),
                'type': n.notification_type,
                'priority': n.priority,
                'title': n.title,
                'message': n.message,
                'is_read': n.is_read,
                'created_at': n.created_at.isoformat(),
                'instance_type': n.instance_type,
                'instance_id': n.instance_id,
            } for n in notifications]

        except Exception as e:
            logger.error(f"Failed to get user notifications: {e}")
            return []

    @staticmethod
    def mark_notifications_read(user, notification_ids: List[str]):
        """Mark notifications as read"""
        try:
            WorkflowNotification.objects.filter(
                recipient=user,
                id__in=notification_ids
            ).update(is_read=True, read_at=timezone.now())

        except Exception as e:
            logger.error(f"Failed to mark notifications as read: {e}")
