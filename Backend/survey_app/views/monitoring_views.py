"""
Survey App - Monitoring Views
==============================
Views for monitoring survey responses and non-respondents (Problem 2).
These views allow admins/superadmins to track who hasn't responded to surveys.
"""

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse
from django.utils import timezone
import csv

from ..models import SurveyTemplate
from ..serializers import NonRespondentSerializer, SurveyStatisticsSerializer
from ..permissions import IsSurveyAdmin
from ..utils import get_survey_non_respondents, get_survey_response_statistics


class SurveyNonRespondentsView(APIView):
    """
    GET /api/surveys/{survey_id}/non-respondents/
    
    Get list of alumni who have not responded to a specific survey.
    Supports filtering by program, year_graduated, etc.
    
    Query Parameters:
        - program: Filter by program name (case-insensitive partial match)
        - year_graduated: Filter by specific graduation year
        - year_graduated_from: Filter by graduation year range (from)
        - year_graduated_to: Filter by graduation year range (to)
        - export: If 'csv', download as CSV file
    """
    permission_classes = [IsSurveyAdmin]
    
    def get(self, request, survey_id):
        """Get non-respondents for a survey with optional filters"""
        try:
            survey = SurveyTemplate.objects.get(id=survey_id)
        except SurveyTemplate.DoesNotExist:
            return Response(
                {'error': 'Survey not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Build filters from query params
        filters = {}
        if request.query_params.get('program'):
            filters['program'] = request.query_params.get('program')
        if request.query_params.get('year_graduated'):
            filters['year_graduated'] = request.query_params.get('year_graduated')
        if request.query_params.get('year_graduated_from'):
            filters['year_graduated_from'] = request.query_params.get('year_graduated_from')
        if request.query_params.get('year_graduated_to'):
            filters['year_graduated_to'] = request.query_params.get('year_graduated_to')
        
        # Get non-respondents
        non_respondents = get_survey_non_respondents(survey, filters)
        
        # Check if export to CSV is requested
        if request.query_params.get('export') == 'csv':
            return self._export_to_csv(non_respondents, survey)
        
        # Serialize and return JSON response
        serializer = NonRespondentSerializer(non_respondents, many=True)
        
        # Get statistics
        stats = get_survey_response_statistics(survey)
        
        return Response({
            'survey': {
                'id': survey.id,
                'name': survey.name,
                'description': survey.description,
            },
            'statistics': stats,
            'non_respondents': serializer.data,
            'count': non_respondents.count(),
            'filters_applied': filters
        })
    
    def _export_to_csv(self, non_respondents, survey):
        """Export non-respondents to CSV file"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="non_respondents_{survey.id}_{timezone.now().strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        
        # Write header
        writer.writerow([
            'ID',
            'Email',
            'First Name',
            'Last Name',
            'Program',
            'Year Graduated',
            'Contact Number',
            'Last Login',
            'Date Joined'
        ])
        
        # Write data rows
        for user in non_respondents:
            writer.writerow([
                user.id,
                user.email,
                user.first_name,
                user.last_name,
                user.program or '',
                user.year_graduated or '',
                user.contact_number or '',
                user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else 'Never',
                user.date_joined.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        return response


class SurveyStatisticsView(APIView):
    """
    GET /api/survey/{survey_id}/statistics/
    
    Get response statistics for a specific survey.
    Shows total alumni, respondents, non-respondents, and response rate.
    Supports optional filtering by program and graduation year.
    """
    permission_classes = [IsSurveyAdmin]
    
    def get(self, request, survey_id):
        """Get statistics for a survey with optional filters"""
        try:
            survey = SurveyTemplate.objects.get(id=survey_id)
        except SurveyTemplate.DoesNotExist:
            return Response(
                {'error': 'Survey not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Extract filter parameters
        programs = request.query_params.get('programs', '').split(',') if request.query_params.get('programs') else []
        graduation_years_str = request.query_params.get('graduation_years', '').split(',') if request.query_params.get('graduation_years') else []
        
        # Convert graduation years to integers
        graduation_years = []
        for year_str in graduation_years_str:
            try:
                graduation_years.append(int(year_str))
            except ValueError:
                pass
        
        # Clean empty strings from programs
        programs = [p.strip() for p in programs if p.strip()]
        
        # Get statistics with filters
        stats = get_survey_response_statistics(
            survey,
            programs=programs if programs else None,
            graduation_years=graduation_years if graduation_years else None
        )
        stats['survey_id'] = survey.id
        stats['survey_name'] = survey.name
        
        # Serialize
        serializer = SurveyStatisticsSerializer(stats)
        
        return Response(serializer.data)


class AllSurveysStatisticsView(APIView):
    """
    GET /api/surveys/statistics/all/
    
    Get response statistics for all published surveys.
    Useful for dashboard overview.
    """
    permission_classes = [IsSurveyAdmin]
    
    def get(self, request):
        """Get statistics for all surveys"""
        surveys = SurveyTemplate.objects.filter(
            is_published=True,
            is_active=True
        ).order_by('-created_at')
        
        all_stats = []
        for survey in surveys:
            stats = get_survey_response_statistics(survey)
            stats['survey_id'] = survey.id
            stats['survey_name'] = survey.name
            all_stats.append(stats)
        
        # Serialize
        serializer = SurveyStatisticsSerializer(all_stats, many=True)
        
        return Response({
            'count': len(all_stats),
            'results': serializer.data
        })


class NotifyNonRespondentsView(APIView):
    """
    POST /api/surveys/{survey_id}/notify-non-respondents/
    
    Send reminder notifications to alumni who haven't responded to a survey.
    Supports bulk notifications by filters or specific recipient IDs.
    Can send both in-app notifications and email reminders.
    
    Request Body:
        - recipient_ids: Optional list of specific user IDs to notify
        - filters: Optional dict with program, year_graduated, year_graduated_from, year_graduated_to
        - title: Optional custom notification title (default: "Survey Reminder")
        - message: Optional custom message (default includes survey name)
        - link_route: Optional route (default: "/alumni/survey")
        - link_params: Optional dict (default: {surveyId: <id>})
        - send_email: Optional boolean (default: true) - whether to send email reminders
    
    Returns:
        - notified: Count of users notified
        - skipped: Count of users skipped (errors)
        - total_candidates: Total non-respondents matching criteria
        - email_status: Email sending status (if enabled)
    """
    permission_classes = [IsSurveyAdmin]
    
    def post(self, request, survey_id):
        """Send notifications and emails to non-respondents"""
        from notifications_app.utils import create_bulk_notifications
        from notifications_app.tasks import send_survey_reminder_emails_bulk
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        try:
            survey = SurveyTemplate.objects.get(id=survey_id)
        except SurveyTemplate.DoesNotExist:
            return Response(
                {'error': 'Survey not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get parameters from request body
        recipient_ids = request.data.get('recipient_ids')
        filters = request.data.get('filters', {})
        title = request.data.get('title', 'Survey Reminder')
        message = request.data.get('message')
        link_route = request.data.get('link_route', '/alumni/survey')
        link_params = request.data.get('link_params', {'surveyId': survey_id})
        send_email = request.data.get('send_email', True)  # Default to True
        
        # Default message if not provided
        if not message:
            message = f"Reminder: Please complete the '{survey.name}' survey. Your response is important to us!"
        
        # Get non-respondents based on filters or specific IDs
        if recipient_ids:
            # Filter by specific IDs
            non_respondents = User.objects.filter(
                id__in=recipient_ids,
                user_type=3,
                is_approved=True,
                is_active=True
            )
            
            # Double-check they're actually non-respondents
            non_respondents_queryset = get_survey_non_respondents(survey, filters)
            non_respondents = non_respondents.filter(id__in=non_respondents_queryset.values_list('id', flat=True))
        else:
            # Use filters to get non-respondents
            non_respondents = get_survey_non_respondents(survey, filters)
        
        total_candidates = non_respondents.count()
        
        if total_candidates == 0:
            return Response({
                'message': 'No non-respondents found matching the criteria',
                'notified': 0,
                'skipped': 0,
                'total_candidates': 0,
                'email_status': 'skipped - no recipients'
            })
        
        # Send bulk in-app notifications
        created_notifications = create_bulk_notifications(
            users=non_respondents,
            notification_type='survey',
            title=title,
            message=message,
            link_route=link_route,
            link_params=link_params,
            metadata={
                'survey_id': survey.id,
                'survey_name': survey.name,
                'end_at': survey.end_at.isoformat() if survey.end_at else None
            }
        )
        
        notified_count = len(created_notifications)
        skipped_count = total_candidates - notified_count
        
        # Send email reminders if enabled
        email_status = 'disabled'
        if send_email:
            import logging
            logger = logging.getLogger(__name__)
            
            try:
                # Build survey link
                survey_link = request.build_absolute_uri(
                    f"{link_route}?surveyId={survey_id}"
                )
                
                # Get user IDs for email task
                user_ids = list(non_respondents.values_list('id', flat=True))
                
                # Format end date for email (no longer used but kept for compatibility)
                end_date = None
                
                # Try async with Celery, fallback to sync if unavailable
                try:
                    send_survey_reminder_emails_bulk.delay(
                        user_ids=user_ids,
                        survey_name=survey.name,
                        survey_link=survey_link,
                        custom_message=message,
                        end_date=end_date
                    )
                    email_status = f'queued for {len(user_ids)} recipients'
                    logger.info(f"Queued {len(user_ids)} survey reminder emails")
                except Exception as celery_error:
                    # Celery not available, send synchronously
                    logger.info(f"Celery unavailable, sending emails synchronously: {celery_error}")
                    from notifications_app.tasks import send_survey_reminder_email_sync
                    success_count = 0
                    failed_count = 0
                    error_messages = []
                    
                    import time
                    for idx, user_id in enumerate(user_ids):
                        try:
                            result = send_survey_reminder_email_sync(
                                user_id=user_id,
                                survey_name=survey.name,
                                survey_link=survey_link,
                                custom_message=message,
                                end_date=end_date
                            )
                            if result['status'] == 'success':
                                success_count += 1
                                logger.info(f"Email sent to user {user_id}")
                            else:
                                failed_count += 1
                                error_messages.append(f"User {user_id}: {result.get('message', 'Unknown error')}")
                        except Exception as email_error:
                            failed_count += 1
                            error_msg = str(email_error)
                            error_messages.append(f"User {user_id}: {error_msg}")
                            logger.error(f"Failed to send email to user {user_id}: {error_msg}")
                        
                        # Small delay between emails to avoid connection issues
                        if idx < len(user_ids) - 1:
                            time.sleep(1)
                    
                    if success_count > 0:
                        email_status = f'sent to {success_count} users'
                        if failed_count > 0:
                            email_status += f' ({failed_count} failed)'
                    else:
                        email_status = f'failed: {error_messages[0] if error_messages else "Unknown error"}'
                
            except Exception as e:
                error_msg = str(e)
                logger.error(f"Email sending failed: {error_msg}")
                email_status = f'error: {error_msg}'
        
        return Response({
            'message': f'Successfully sent {notified_count} notifications',
            'notified': notified_count,
            'skipped': skipped_count,
            'total_candidates': total_candidates,
            'email_status': email_status,
            'survey': {
                'id': survey.id,
                'name': survey.name
            }
        })


class NotifySingleNonRespondentView(APIView):
    """
    POST /api/surveys/{survey_id}/notify-user/
    
    Send a reminder notification to a single non-respondent.
    Can send both in-app notification and email reminder.
    
    Request Body:
        - user_id: Required user ID
        - title: Optional custom title (default: "Survey Reminder")
        - message: Optional custom message (default includes survey name)
        - link_route: Optional route (default: "/alumni/survey")
        - link_params: Optional dict (default: {surveyId: <id>})
        - send_email: Optional boolean (default: true) - whether to send email reminder
    """
    permission_classes = [IsSurveyAdmin]
    
    def post(self, request, survey_id):
        """Send notification and email to a single user"""
        from django.contrib.auth import get_user_model
        from notifications_app.utils import create_notification
        from notifications_app.tasks import send_survey_reminder_email
        
        User = get_user_model()
        
        try:
            survey = SurveyTemplate.objects.get(id=survey_id)
        except SurveyTemplate.DoesNotExist:
            return Response(
                {'error': 'Survey not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        user_id = request.data.get('user_id')
        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(id=user_id, user_type=3, is_approved=True, is_active=True)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found or not an approved alumni'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verify user is actually a non-respondent
        non_respondents = get_survey_non_respondents(survey, {})
        if not non_respondents.filter(id=user_id).exists():
            return Response(
                {'error': 'User has already responded to this survey'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get custom notification parameters
        title = request.data.get('title', 'Survey Reminder')
        message = request.data.get('message')
        link_route = request.data.get('link_route', '/alumni/survey')
        link_params = request.data.get('link_params', {'surveyId': survey_id})
        send_email = request.data.get('send_email', True)  # Default to True
        
        if not message:
            message = f"Reminder: Please complete the '{survey.name}' survey. Your response is important to us!"
        
        # Send in-app notification
        try:
            notification = create_notification(
                user=user,
                notification_type='survey',
                title=title,
                message=message,
                link_route=link_route,
                link_params=link_params,
                metadata={
                    'survey_id': survey.id,
                    'survey_name': survey.name,
                    'end_at': survey.end_at.isoformat() if survey.end_at else None
                }
            )
            
            # Send email reminder if enabled
            email_status = 'disabled'
            if send_email:
                try:
                    # Build survey link
                    survey_link = request.build_absolute_uri(
                        f"{link_route}?surveyId={survey_id}"
                    )
                    
                    # Format end date for email
                    end_date = None
                    if survey.end_at:
                        end_date = survey.end_at.strftime('%B %d, %Y at %I:%M %p')
                    
                    # Try async with Celery, fallback to sync if unavailable
                    try:
                        send_survey_reminder_email.delay(
                            user_id=user.id,
                            survey_name=survey.name,
                            survey_link=survey_link,
                            custom_message=message,
                            end_date=end_date
                        )
                        email_status = 'queued'
                    except Exception:
                        # Celery not available, send synchronously
                        from notifications_app.tasks import send_survey_reminder_email_sync
                        result = send_survey_reminder_email_sync(
                            user_id=user.id,
                            survey_name=survey.name,
                            survey_link=survey_link,
                            custom_message=message,
                            end_date=end_date
                        )
                        email_status = 'sent' if result['status'] == 'success' else result['status']
                    
                except Exception as e:
                    email_status = f'error: {str(e)}'
            
            return Response({
                'message': f'Notification sent to {user.get_full_name() or user.email}',
                'notification_id': notification.id,
                'email_status': email_status,
                'user': {
                    'id': user.id,
                    'name': user.get_full_name() or user.email,
                    'email': user.email
                }
            })
            
        except Exception as e:
            return Response(
                {'error': f'Failed to send notification: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
