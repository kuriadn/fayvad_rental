"""
Audit Log Service
Tracks all workflow transitions and business events
"""

from typing import Dict, List, Any, Optional
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
import json
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class WorkflowAuditLog(models.Model):
    """
    Model for storing workflow audit logs
    """

    EVENT_TYPES = [
        ('transition', 'State Transition'),
        ('validation', 'Validation Event'),
        ('notification', 'Notification Sent'),
        ('error', 'Error Event'),
        ('manual', 'Manual Action'),
    ]

    instance_type = models.CharField(max_length=100)  # Model class name
    instance_id = models.CharField(max_length=50)     # Instance UUID
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    event_name = models.CharField(max_length=100)     # e.g., 'assign_technician'

    old_state = models.CharField(max_length=50, blank=True, null=True)
    new_state = models.CharField(max_length=50, blank=True, null=True)

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    user_name = models.CharField(max_length=200, blank=True)  # Store name in case user is deleted

    metadata = models.JSONField(default=dict)  # Additional event data
    notes = models.TextField(blank=True)       # Human-readable description

    timestamp = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['instance_type', 'instance_id']),
            models.Index(fields=['event_type']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"{self.instance_type} {self.instance_id}: {self.event_name} at {self.timestamp}"

    def save(self, *args, **kwargs):
        # Store user name for audit trail integrity
        if self.user and not self.user_name:
            self.user_name = self.user.get_full_name() or self.user.username
        super().save(*args, **kwargs)


class AuditLogService:
    """
    Service for managing workflow audit logs
    """

    @staticmethod
    def log_workflow_transition(instance_type: str,
                              instance_id: str,
                              event: str,
                              old_state: str,
                              new_state: str,
                              user,
                              metadata: Optional[Dict[str, Any]] = None,
                              ip_address: Optional[str] = None,
                              notes: Optional[str] = None) -> WorkflowAuditLog:
        """
        Log a workflow state transition
        """
        try:
            # Make metadata JSON serializable
            from decimal import Decimal
            def make_serializable(obj):
                if isinstance(obj, Decimal):
                    return float(obj)
                elif hasattr(obj, '__dict__'):
                    # For model instances, just store the string representation
                    return str(obj)
                else:
                    return obj

            serializable_metadata = {}
            for key, value in (metadata or {}).items():
                try:
                    # Test if it's JSON serializable
                    json.dumps(value)
                    serializable_metadata[key] = value
                except (TypeError, ValueError):
                    # If not serializable, convert it
                    serializable_metadata[key] = make_serializable(value)

            log_entry = WorkflowAuditLog.objects.create(
                instance_type=instance_type,
                instance_id=instance_id,
                event_type='transition',
                event_name=event,
                old_state=old_state,
                new_state=new_state,
                user=user,
                metadata=serializable_metadata,
                notes=notes or f"State changed from {old_state} to {new_state}",
                ip_address=ip_address,
            )

            logger.info(f"Workflow transition logged: {instance_type} {instance_id} - {event}")
            return log_entry

        except Exception as e:
            logger.error(f"Failed to log workflow transition: {e}")
            # Don't raise exception - audit logging failure shouldn't break business logic
            return None

    @staticmethod
    def log_event(instance_type: str,
                 instance_id: str,
                 event_type: str,
                 event_name: str,
                 user: Optional[User] = None,
                 metadata: Optional[Dict[str, Any]] = None,
                 notes: Optional[str] = None,
                 ip_address: Optional[str] = None) -> WorkflowAuditLog:
        """
        Log a general workflow event
        """
        try:
            log_entry = WorkflowAuditLog.objects.create(
                instance_type=instance_type,
                instance_id=instance_id,
                event_type=event_type,
                event_name=event_name,
                user=user,
                metadata=metadata or {},
                notes=notes,
                ip_address=ip_address,
            )

            logger.info(f"Workflow event logged: {instance_type} {instance_id} - {event_name}")
            return log_entry

        except Exception as e:
            logger.error(f"Failed to log workflow event: {e}")
            return None

    @staticmethod
    def get_workflow_history(instance_type: str, instance_id: str) -> List[Dict[str, Any]]:
        """
        Get complete workflow history for an instance
        """
        try:
            logs = WorkflowAuditLog.objects.filter(
                instance_type=instance_type,
                instance_id=instance_id
            ).select_related('user').order_by('timestamp')

            history = []
            for log in logs:
                history.append({
                    'id': str(log.id),
                    'event_type': log.event_type,
                    'event_name': log.event_name,
                    'old_state': log.old_state,
                    'new_state': log.new_state,
                    'user': log.user_name or 'System',
                    'user_id': str(log.user.id) if log.user else None,
                    'metadata': log.metadata,
                    'notes': log.notes,
                    'timestamp': log.timestamp.isoformat(),
                })

            return history

        except Exception as e:
            logger.error(f"Failed to get workflow history: {e}")
            return []

    @staticmethod
    def get_events(instance_type: str, instance_id: str, event_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get events for an instance, optionally filtered by event_type
        """
        try:
            query = WorkflowAuditLog.objects.filter(
                instance_type=instance_type,
                instance_id=instance_id
            )

            if event_type:
                query = query.filter(event_type=event_type)

            logs = query.select_related('user').order_by('-timestamp')

            events = []
            for log in logs:
                events.append({
                    'id': str(log.id),
                    'event_type': log.event_type,
                    'event_name': log.event_name,
                    'title': log.event_name.replace('_', ' ').title(),
                    'message': log.notes or f"{log.event_name.replace('_', ' ').title()} event",
                    'user': log.user_name or 'System',
                    'timestamp': log.timestamp.isoformat(),
                    'reason': log.metadata.get('escalation_reason') if log.metadata else None,
                })

            return events

        except Exception as e:
            logger.error(f"Failed to get events: {e}")
            return []

    @staticmethod
    def get_recent_activity(user: Optional[User] = None,
                          days: int = 7,
                          event_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Get recent workflow activity
        """
        try:
            since_date = timezone.now() - timezone.timedelta(days=days)

            queryset = WorkflowAuditLog.objects.filter(
                timestamp__gte=since_date
            ).select_related('user').order_by('-timestamp')

            if user:
                queryset = queryset.filter(user=user)

            if event_types:
                queryset = queryset.filter(event_type__in=event_types)

            logs = queryset[:50]  # Limit to recent 50 entries

            activity = []
            for log in logs:
                activity.append({
                    'instance_type': log.instance_type,
                    'instance_id': log.instance_id,
                    'event_type': log.event_type,
                    'event_name': log.event_name,
                    'user': log.user_name or 'System',
                    'notes': log.notes,
                    'timestamp': log.timestamp.isoformat(),
                })

            return activity

        except Exception as e:
            logger.error(f"Failed to get recent activity: {e}")
            return []

    @staticmethod
    def get_audit_summary(instance_type: str = None,
                        event_type: str = None,
                        days: int = 30) -> Dict[str, Any]:
        """
        Get audit summary statistics
        """
        try:
            since_date = timezone.now() - timezone.timedelta(days=days)

            queryset = WorkflowAuditLog.objects.filter(timestamp__gte=since_date)

            if instance_type:
                queryset = queryset.filter(instance_type=instance_type)

            if event_type:
                queryset = queryset.filter(event_type=event_type)

            total_events = queryset.count()

            # Group by event type
            event_counts = {}
            for log in queryset.values('event_type').annotate(count=models.Count('id')):
                event_counts[log['event_type']] = log['count']

            # Group by instance type
            instance_counts = {}
            for log in queryset.values('instance_type').annotate(count=models.Count('id')):
                instance_counts[log['instance_type']] = log['count']

            # Recent transitions
            transitions = queryset.filter(
                event_type='transition'
            ).order_by('-timestamp')[:10]

            recent_transitions = []
            for t in transitions:
                recent_transitions.append({
                    'instance_type': t.instance_type,
                    'instance_id': t.instance_id,
                    'event': t.event_name,
                    'old_state': t.old_state,
                    'new_state': t.new_state,
                    'user': t.user_name or 'System',
                    'timestamp': t.timestamp.isoformat(),
                })

            return {
                'total_events': total_events,
                'event_counts': event_counts,
                'instance_counts': instance_counts,
                'recent_transitions': recent_transitions,
                'period_days': days,
            }

        except Exception as e:
            logger.error(f"Failed to get audit summary: {e}")
            return {
                'total_events': 0,
                'event_counts': {},
                'instance_counts': {},
                'recent_transitions': [],
                'period_days': days,
            }
