"""
Notification Email Tasks
========================
Celery tasks for sending notification emails asynchronously.
"""

from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth import get_user_model
from django.conf import settings
import logging
import socket

from .email_templates import get_survey_reminder_email_template

User = get_user_model()
logger = logging.getLogger(__name__)

# Set default socket timeout to prevent hanging
socket.setdefaulttimeout(30)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={'max_retries': 3}
)
def send_survey_reminder_email(
    self,
    user_id,
    survey_name,
    survey_link,
    custom_message=None,
    end_date=None
):
    """
    Send survey reminder email to a single user.
    
    Args:
        user_id: ID of the user to email
        survey_name: Name of the survey
        survey_link: Full URL to the survey
        custom_message: Optional custom message
        end_date: Optional survey end date (string)
    
    Returns:
        dict: Status message
    """
    try:
        user = User.objects.get(id=user_id)
        
        if not user.email:
            logger.warning(f"User {user_id} has no email address")
            return {
                'status': 'skipped',
                'message': f'User {user_id} has no email address'
            }
        
        # Generate email content
        subject, html_content, text_content = get_survey_reminder_email_template(
            user=user,
            survey_name=survey_name,
            survey_link=survey_link,
            custom_message=custom_message,
            end_date=end_date
        )
        
        # Create email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        email.attach_alternative(html_content, "text/html")
        
        # Send email
        email.send(fail_silently=False)
        
        logger.info(f"Survey reminder email sent to {user.email} for survey '{survey_name}'")
        
        return {
            'status': 'success',
            'message': f'Email sent to {user.email}',
            'user_id': user_id
        }
        
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found")
        return {
            'status': 'error',
            'message': f'User {user_id} not found'
        }
    except Exception as e:
        logger.error(f"Failed to send survey reminder email to user {user_id}: {str(e)}")
        raise


@shared_task(bind=True)
def send_survey_reminder_emails_bulk(
    self,
    user_ids,
    survey_name,
    survey_link,
    custom_message=None,
    end_date=None
):
    """
    Send survey reminder emails to multiple users.
    
    Args:
        user_ids: List of user IDs to email
        survey_name: Name of the survey
        survey_link: Full URL to the survey
        custom_message: Optional custom message
        end_date: Optional survey end date (string)
    
    Returns:
        dict: Summary of send results
    """
    results = {
        'total': len(user_ids),
        'success': 0,
        'skipped': 0,
        'failed': 0,
        'errors': []
    }
    
    logger.info(f"Starting bulk survey reminder emails for {len(user_ids)} users")
    
    for user_id in user_ids:
        try:
            result = send_survey_reminder_email.apply(
                args=[user_id, survey_name, survey_link, custom_message, end_date]
            )
            
            if result.get('status') == 'success':
                results['success'] += 1
            elif result.get('status') == 'skipped':
                results['skipped'] += 1
            else:
                results['failed'] += 1
                results['errors'].append({
                    'user_id': user_id,
                    'message': result.get('message', 'Unknown error')
                })
                
        except Exception as e:
            results['failed'] += 1
            results['errors'].append({
                'user_id': user_id,
                'message': str(e)
            })
            logger.error(f"Failed to send email to user {user_id}: {str(e)}")
    
    logger.info(
        f"Bulk email complete: {results['success']} sent, "
        f"{results['skipped']} skipped, {results['failed']} failed"
    )
    
    return results


def send_survey_reminder_email_sync(
    user_id,
    survey_name,
    survey_link,
    custom_message=None,
    end_date=None
):
    """
    Send survey reminder email synchronously (for testing or when Celery is unavailable).
    
    Args:
        user_id: ID of the user to email
        survey_name: Name of the survey
        survey_link: Full URL to the survey
        custom_message: Optional custom message
        end_date: Optional survey end date (string)
    
    Returns:
        dict: Status message
    """
    try:
        user = User.objects.get(id=user_id)
        
        if not user.email:
            logger.warning(f"User {user_id} has no email address")
            return {
                'status': 'skipped',
                'message': f'User {user_id} has no email address'
            }
        
        # Generate email content
        subject, html_content, text_content = get_survey_reminder_email_template(
            user=user,
            survey_name=survey_name,
            survey_link=survey_link,
            custom_message=custom_message,
            end_date=end_date
        )
        
        # Create and send email with retry logic
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        email.attach_alternative(html_content, "text/html")
        
        # Try to send with retries
        max_retries = 3
        for attempt in range(max_retries):
            try:
                email.send(fail_silently=False)
                logger.info(f"Survey reminder email sent (sync) to {user.email}")
                return {
                    'status': 'success',
                    'message': f'Email sent to {user.email}',
                    'user_id': user_id
                }
            except Exception as send_error:
                if attempt < max_retries - 1:
                    import time
                    time.sleep(2)  # Wait 2 seconds before retry
                    logger.warning(f"Email send attempt {attempt + 1} failed, retrying...")
                else:
                    raise send_error
        
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found")
        return {
            'status': 'error',
            'message': f'User {user_id} not found'
        }
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Failed to send survey reminder email to user {user_id}: {error_msg}")
        
        # Check if it's an SMTP connection error
        if 'refused' in error_msg.lower() or 'connection' in error_msg.lower():
            return {
                'status': 'error',
                'message': f'SMTP connection failed. Please check email settings or start Celery worker for background processing.'
            }
        
        return {
            'status': 'error',
            'message': error_msg
        }
