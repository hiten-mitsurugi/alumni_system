"""
Celery tasks for background processing
"""
from celery import shared_task
from django.core.cache import cache
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_approval_email_task(user_id, user_email, user_first_name, user_last_name, user_username):
    """
    Send approval email in background
    """
    try:
        from .email_templates.approval_email import get_approval_email_template
        
        # Create a minimal user object for template
        class UserData:
            def __init__(self, first_name, last_name, email, username):
                self.first_name = first_name
                self.last_name = last_name
                self.email = email
                self.username = username
        
        user = UserData(user_first_name, user_last_name, user_email, user_username)
        subject, html_content, text_content = get_approval_email_template(user)
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user_email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        
        logger.info(f"Approval email sent successfully to {user_email} (User ID: {user_id})")
        return {'success': True, 'email': user_email}
        
    except Exception as e:
        logger.error(f"Failed to send approval email to {user_email}: {str(e)}")
        return {'success': False, 'error': str(e)}


@shared_task
def send_rejection_email_task(user_email, user_first_name, user_last_name, user_username):
    """
    Send rejection email in background
    """
    try:
        from .email_templates.approval_email import get_rejection_email_template
        
        class UserData:
            def __init__(self, first_name, last_name, email, username):
                self.first_name = first_name
                self.last_name = last_name
                self.email = email
                self.username = username
        
        user = UserData(user_first_name, user_last_name, user_email, user_username)
        subject, html_content, text_content = get_rejection_email_template(user)
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user_email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        
        logger.info(f"Rejection email sent successfully to {user_email}")
        return {'success': True, 'email': user_email}
        
    except Exception as e:
        logger.error(f"Failed to send rejection email to {user_email}: {str(e)}")
        return {'success': False, 'error': str(e)}


@shared_task
def clear_approval_caches_task(user_id, year_graduated, program, first_name, last_name):
    """
    Clear caches in background - simplified version
    """
    try:
        # Clear main caches
        cache.delete('approved_alumni_list')
        cache.delete('pending_alumni_list')
        cache.delete(f'user_detail_{user_id}')
        
        # Clear only the most common filter combinations (reduced from 162 to ~20)
        common_filters = [
            ('', '', ''),  # No filters
            ('employed_locally', '', ''),
            ('employed_internationally', '', ''),
            ('self_employed', '', ''),
            ('unemployed', '', ''),
        ]
        
        for emp_status, gender, status_filter in common_filters:
            cache_key = f"approved_alumni_list_{emp_status}_{gender}_{year_graduated or ''}_{program or ''}_{status_filter}_"
            cache.delete(cache_key)
        
        logger.info(f"Cache cleared for user {user_id}")
        return {'success': True, 'cleared_keys': len(common_filters) + 3}
        
    except Exception as e:
        logger.error(f"Failed to clear caches for user {user_id}: {str(e)}")
        return {'success': False, 'error': str(e)}
