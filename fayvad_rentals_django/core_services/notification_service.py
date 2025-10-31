"""
Simple Notification Service
Replaces complex workflow triggers with basic email notifications
"""

from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from typing import List, Dict, Any
from django.contrib.auth import get_user_model

User = get_user_model()


class SimpleNotificationService:
    """
    Simple notification service for rental management
    Basic email notifications for overdue items
    """

    @staticmethod
    def send_overdue_maintenance_notification(overdue_requests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Send notification about overdue maintenance requests
        """
        try:
            if not overdue_requests:
                return {'success': True, 'message': 'No overdue requests'}

            # Get staff users to notify
            staff_users = User.objects.filter(
                staff_profile__isnull=False,
                staff_profile__is_active_staff=True,
                is_active=True
            )

            recipient_emails = [user.email for user in staff_users if user.email]

            if not recipient_emails:
                return {'success': False, 'error': 'No staff emails found'}

            # Prepare email content
            context = {
                'overdue_requests': overdue_requests,
                'count': len(overdue_requests),
                'site_name': 'Fayvad Rentals'
            }

            subject = f'Overdue Maintenance Alert - {len(overdue_requests)} requests'
            html_message = render_to_string('emails/overdue_maintenance.html', context)
            plain_message = render_to_string('emails/overdue_maintenance.txt', context)

            # Send email
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_emails,
                html_message=html_message,
                fail_silently=False
            )

            return {
                'success': True,
                'message': f'Notification sent to {len(recipient_emails)} staff members'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    @staticmethod
    def send_overdue_payments_notification(overdue_payments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Send notification about overdue payments
        """
        try:
            if not overdue_payments:
                return {'success': True, 'message': 'No overdue payments'}

            # Get staff users to notify
            staff_users = User.objects.filter(
                staff_profile__isnull=False,
                staff_profile__is_active_staff=True,
                is_active=True
            )

            recipient_emails = [user.email for user in staff_users if user.email]

            if not recipient_emails:
                return {'success': False, 'error': 'No staff emails found'}

            # Calculate total amount
            total_amount = sum(payment.get('amount', 0) for payment in overdue_payments)

            # Prepare email content
            context = {
                'overdue_payments': overdue_payments,
                'count': len(overdue_payments),
                'total_amount': total_amount,
                'site_name': 'Fayvad Rentals'
            }

            subject = f'Overdue Payments Alert - {len(overdue_payments)} payments'
            html_message = render_to_string('emails/overdue_payments.html', context)
            plain_message = render_to_string('emails/overdue_payments.txt', context)

            # Send email
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_emails,
                html_message=html_message,
                fail_silently=False
            )

            return {
                'success': True,
                'message': f'Notification sent to {len(recipient_emails)} staff members'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    @staticmethod
    def send_daily_summary() -> Dict[str, Any]:
        """
        Send daily summary of system status
        """
        try:
            from maintenance.models import MaintenanceRequest
            from payments.models import Payment
            from rentals.models import RentalAgreement

            # Gather summary data
            summary = {
                'pending_maintenance': MaintenanceRequest.objects.filter(
                    status__in=['pending', 'in_progress']
                ).count(),
                'pending_payments': Payment.objects.filter(status='pending').count(),
                'active_agreements': RentalAgreement.objects.filter(status='active').count(),
                'total_revenue_today': float(Payment.objects.filter(
                    status='completed',
                    updated_at__date=timezone.now().date()
                ).aggregate(total=Sum('amount'))['total'] or 0)
            }

            # Get staff users
            staff_users = User.objects.filter(
                staff_profile__isnull=False,
                staff_profile__is_active_staff=True,
                is_active=True
            )

            recipient_emails = [user.email for user in staff_users if user.email]

            if not recipient_emails:
                return {'success': False, 'error': 'No staff emails found'}

            # Prepare email content
            context = {
                'summary': summary,
                'site_name': 'Fayvad Rentals',
                'date': timezone.now().date()
            }

            subject = f'Daily Summary - {timezone.now().date()}'
            html_message = render_to_string('emails/daily_summary.html', context)
            plain_message = render_to_string('emails/daily_summary.txt', context)

            # Send email
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_emails,
                html_message=html_message,
                fail_silently=False
            )

            return {
                'success': True,
                'message': f'Daily summary sent to {len(recipient_emails)} staff members'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}
