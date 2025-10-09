from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.generics import ListAPIView, RetrieveAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from .email_templates.approval_email import get_approval_email_template, get_rejection_email_template
from django.core.cache import cache
from django.db.models import Q
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import transaction
from django.utils import timezone
import pandas as pd
import io
from datetime import datetime
from .models import CustomUser, Skill, WorkHistory, AlumniDirectory, Profile
from .status_cache import set_user_online, set_user_offline, get_user_status
from .serializers import (
    RegisterSerializer, UserDetailSerializer, UserCreateSerializer,
    SkillSerializer, WorkHistorySerializer, AlumniDirectoryCheckSerializer,
    ProfileSerializer, UserSearchSerializer, AlumniDirectorySerializer
)
from .permissions import IsAdminOrSuperAdmin
from .utils import generate_token, confirm_token
from django.urls import reverse
import logging
from django.contrib.auth import get_user_model
from rest_framework import viewsets

logger = logging.getLogger(__name__)

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        import json
        
        # Add detailed logging for debugging
        logger.info("=== REGISTRATION ATTEMPT ===")
        logger.info(f"Request data keys: {list(request.data.keys())}")
        logger.info(f"Alumni exists value: {request.data.get('alumni_exists')}")
        logger.info(f"Survey responses: {request.data.get('survey_responses')}")
        logger.info(f"Email: {request.data.get('email')}")
        logger.info(f"Employment status: {request.data.get('employment_status')}")
        logger.info(f"Gender: {request.data.get('gender')}")
        logger.info(f"Civil status: {request.data.get('civil_status')}")
        
        # Parse JSON fields from FormData
        data = request.data.copy()
        
        # Parse address data if present
        if 'present_address_data' in data and isinstance(data['present_address_data'], str):
            try:
                data['present_address_data'] = json.loads(data['present_address_data'])
                logger.info(f"Parsed present_address_data: {data['present_address_data']}")
            except json.JSONDecodeError:
                logger.error("Failed to parse present_address_data JSON")
                
        if 'permanent_address_data' in data and isinstance(data['permanent_address_data'], str):
            try:
                data['permanent_address_data'] = json.loads(data['permanent_address_data'])
                logger.info(f"Parsed permanent_address_data: {data['permanent_address_data']}")
            except json.JSONDecodeError:
                logger.error("Failed to parse permanent_address_data JSON")
        
        serializer = RegisterSerializer(data=data)

        if serializer.is_valid():
            try:
                with transaction.atomic():
                    user = serializer.save()
                    logger.info(f"User created successfully: {user.email}")

                    try:
                        channel_layer = get_channel_layer()
                        async_to_sync(channel_layer.group_send)(
                            'admin_notifications',
                            {
                                'type': 'send_notification',
                                'message': {
                                    'type': 'new_user',
                                    'user_id': user.id,
                                    'email': user.email,
                                    'first_name': user.first_name,
                                    'last_name': user.last_name
                                }
                            }
                        )
                    except Exception as ws_error:
                        logger.error(f"WebSocket notification failed in RegisterView: {str(ws_error)}")

                return Response(
                    {'message': 'User registered successfully, pending approval.'},
                    status=status.HTTP_201_CREATED
                )

            except Exception as db_error:
                logger.error(f"Database error during registration: {str(db_error)}")
                return Response(
                    {'error': 'An error occurred while processing your registration.'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        # Log validation errors for debugging
        logger.error("=== REGISTRATION VALIDATION FAILED ===")
        logger.error(f"Serializer errors: {serializer.errors}")
        for field, errors in serializer.errors.items():
            logger.error(f"Field '{field}': {errors}")
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ApproveUserView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def post(self, request, user_id):
        try:
            with transaction.atomic():
                user = CustomUser.objects.get(id=user_id, user_type=3, is_approved=False)
                user.is_approved = True
                user.save()
                
                # Clear all related caches after approval
                cache.delete('approved_alumni_list')
                cache.delete('pending_alumni_list')
                
                # Clear all cached variations of approved_alumni_list (comprehensive clearing)
                # This ensures approved user appears in filtered lists immediately
                cache_patterns = [
                    'approved_alumni_list_*',  # All filter combinations
                    f'user_detail_{user.id}',  # User-specific cache
                ]
                
                # Django cache doesn't support pattern deletion, so we clear key types we know exist
                # Clear common filter combinations to ensure immediate visibility
                for emp_status in ['', 'employed_locally', 'employed_internationally', 'self_employed', 'unemployed', 'retired']:
                    for gender in ['', 'male', 'female']:
                        for status_filter in ['', 'active', 'blocked']:
                            cache_key = f"approved_alumni_list_{emp_status}_{gender}_{user.year_graduated or ''}_{user.program or ''}_{status_filter}_"
                            cache.delete(cache_key)
                            # Also clear with search terms
                            cache.delete(f"{cache_key}{user.first_name.lower()}")
                            cache.delete(f"{cache_key}{user.last_name.lower()}")
            
            # Send approval confirmation email
            try:
                subject, html_content, text_content = get_approval_email_template(user)
                
                # Create email message with both HTML and text versions
                email = EmailMultiAlternatives(
                    subject=subject,
                    body=text_content,  # Plain text version
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[user.email],
                )
                email.attach_alternative(html_content, "text/html")  # HTML version
                email.send(fail_silently=False)
                
                # Log successful email sending
                logger.info(f"Approval email sent successfully to {user.email} (User ID: {user.id})")
                
                # Send WebSocket notification to update admin interfaces
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    'admin_group',
                    {
                        'type': 'notification',
                        'message': f'User {user.first_name} {user.last_name} has been approved.',
                    }
                )
                
                return Response({
                    'message': 'User approved successfully and email notification sent',
                    'email_sent': True
                }, status=status.HTTP_200_OK)
                
            except Exception as email_error:
                # User is still approved even if email fails
                logger.error(f"Failed to send approval email to {user.email}: {str(email_error)}")
                
                # Send WebSocket notification even if email failed
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    'admin_group',
                    {
                        'type': 'notification',
                        'message': f'User {user.first_name} {user.last_name} has been approved.',
                    }
                )
                
                return Response({
                    'message': 'User approved successfully but email notification failed',
                    'email_sent': False,
                    'email_error': str(email_error)
                }, status=status.HTTP_200_OK)
                
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found or already approved'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error approving user {user_id}: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CheckEmailExistsView(APIView):
    """Public endpoint to check if an email is already registered - for use during registration"""
    permission_classes = [AllowAny]  # No authentication required
    
    def get(self, request):
        email = request.query_params.get('email', '').strip()
        
        if not email:
            return Response({'error': 'Email parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            # Check if email already exists
            user_exists = CustomUser.objects.filter(email__iexact=email).exists()
            
            return Response({
                'exists': user_exists,
                'email': email,
                'message': 'Email is already registered' if user_exists else 'Email is available'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error checking email existence for {email}: {str(e)}")
            return Response({'error': 'Unable to check email availability'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ClearCacheView(APIView):
    """Debug view to manually clear all caches"""
    permission_classes = [IsAdminOrSuperAdmin]
    
    def post(self, request):
        try:
            # Clear all known cache keys
            cache_keys = [
                'approved_alumni_list',
                'pending_alumni_list'
            ]
            
            # Clear base cache keys
            for key in cache_keys:
                cache.delete(key)
            
            # Clear filtered cache variations
            filter_combinations = [
                ('', '', '', '', '', ''),  # No filters
                ('employed_locally', '', '', '', '', ''),
                ('employed_internationally', '', '', '', '', ''),
                ('self_employed', '', '', '', '', ''),
                ('unemployed', '', '', '', '', ''),
                ('retired', '', '', '', '', ''),
                ('', 'male', '', '', '', ''),
                ('', 'female', '', '', '', ''),
                ('', '', '', '', 'active', ''),
                ('', '', '', '', 'blocked', ''),
            ]
            
            cleared_count = 0
            for emp, gen, year, prog, stat, search in filter_combinations:
                cache_key = f"approved_alumni_list_{emp}_{gen}_{year}_{prog}_{stat}_{search}"
                if cache.delete(cache_key):
                    cleared_count += 1
            
            return Response({
                'message': f'Cache cleared successfully. {cleared_count} cache keys removed.',
                'cleared_keys': cache_keys
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DebugUsersView(APIView):
    """Debug view to see current users and their status"""
    permission_classes = [IsAdminOrSuperAdmin]
    
    def get(self, request):
        try:
            # Get all users
            all_users = CustomUser.objects.all().values('id', 'email', 'user_type', 'is_approved', 'is_active', 'first_name', 'last_name')
            
            # Get approved alumni specifically
            approved_alumni = CustomUser.objects.filter(user_type=3, is_approved=True).values('id', 'email', 'first_name', 'last_name', 'is_active')
            
            # Get pending alumni
            pending_alumni = CustomUser.objects.filter(user_type=3, is_approved=False).values('id', 'email', 'first_name', 'last_name')
            
            # Check cache status
            cache_info = {
                'approved_alumni_cache': cache.get('approved_alumni_list'),
                'pending_alumni_cache': cache.get('pending_alumni_list')
            }
            
            return Response({
                'all_users': list(all_users),
                'approved_alumni_count': len(approved_alumni),
                'approved_alumni': list(approved_alumni),
                'pending_alumni_count': len(pending_alumni), 
                'pending_alumni': list(pending_alumni),
                'cache_info': cache_info
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ApprovedAlumniListView(ListAPIView):
    serializer_class = UserDetailSerializer
    permission_classes = [IsAdminOrSuperAdmin]

    def get_queryset(self):
        request = self.request
        employment_status = request.query_params.get('employment_status', '').strip().lower()
        gender = request.query_params.get('gender', '').strip().lower()
        year_graduated = request.query_params.get('year_graduated', '').strip()
        program = request.query_params.get('program', '').strip()
        status = request.query_params.get('status', '').strip().lower()
        search = request.query_params.get('search', '').strip()
        
        # Temporarily disable caching to debug approved users issue
        # cache_key = f"approved_alumni_list_{employment_status}_{gender}_{year_graduated}_{program}_{status}_{search}"
        # cached_ids = cache.get(cache_key)
        # if cached_ids is not None:
        #     return CustomUser.objects.filter(id__in=cached_ids)
            
        queryset = CustomUser.objects.filter(user_type=3, is_approved=True)
        
        # Log the base queryset for debugging
        logger.info(f"ApprovedAlumniListView: Base queryset count: {queryset.count()}")
        for user in queryset[:5]:  # Log first 5 users
            logger.info(f"Approved user: {user.id} - {user.email} - {user.first_name} {user.last_name}")
        
        if employment_status:
            queryset = queryset.filter(employment_status__iexact=employment_status)
        if gender:
            queryset = queryset.filter(sex__iexact=gender)
        if year_graduated:
            queryset = queryset.filter(year_graduated=year_graduated)
        if program:
            queryset = queryset.filter(program=program)
        if status:
            if status == 'active':
                queryset = queryset.filter(is_active=True)
            elif status == 'blocked':
                queryset = queryset.filter(is_active=False)
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search)
            )
        
        logger.info(f"ApprovedAlumniListView: Final queryset count after filters: {queryset.count()}")
        
        # Re-enable caching later after fixing the issue
        # user_ids = list(queryset.values_list('id', flat=True))
        # cache.set(cache_key, user_ids, timeout=3600)
        return queryset
class ConfirmTokenView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, token):
        email = cache.get(f'confirm_token_{token}')
        if not email:
            email = confirm_token(token)
        if email:
            try:
                user = CustomUser.objects.get(email=email)
                if user.is_approved:
                    refresh = RefreshToken.for_user(user)
                    cache.delete(f'confirm_token_{token}')
                    return Response({
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                        'user_type': user.user_type,
                    })
                return Response({'error': 'Account not approved'}, status=status.HTTP_403_FORBIDDEN)
            except CustomUser.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)

class CheckAlumniDirectoryView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AlumniDirectoryCheckSerializer(data=request.data)
        if serializer.is_valid():
            return Response({'exists': True}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RejectUserView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def post(self, request, user_id):
        try:
            user = CustomUser.objects.get(id=user_id, user_type=3, is_approved=False)
            
            # Send rejection notification email before deleting
            try:
                subject, html_content, text_content = get_rejection_email_template(user)
                
                # Create email message with both HTML and text versions
                email = EmailMultiAlternatives(
                    subject=subject,
                    body=text_content,  # Plain text version
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[user.email],
                )
                email.attach_alternative(html_content, "text/html")  # HTML version
                email.send(fail_silently=True)  # Don't fail if email sending fails
                
                logger.info(f"Rejection notification email sent to {user.email} (User ID: {user.id})")
                
            except Exception as email_error:
                logger.error(f"Failed to send rejection email to {user.email}: {str(email_error)}")
            
            # Delete the user account
            user_email = user.email
            user.delete()
            
            # Send WebSocket notification
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'user_{user_id}',
                {
                    'type': 'notification',
                    'message': 'Your account application requires additional review.',
                }
            )
            
            # Clear caches
            cache.delete('approved_alumni_list')
            cache.delete('pending_alumni_list')
            
            return Response({
                'message': 'User application rejected and notification email sent',
                'email_sent': True
            }, status=status.HTTP_200_OK)
            
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found or already processed'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error rejecting user {user_id}: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        print(f"🔍 Login attempt - Email: {email}")
        if not email or not password:
            return Response({'detail': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = CustomUser.objects.filter(email=email).first()
            if user is None:
                print(f"❌ No user found with email: {email}")
                return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
            print(f"✅ User found: {user.username} (ID: {user.id})")
            authenticated_user = authenticate(request=request, username=user.username, password=password)
            print(f"🔐 Authentication result: {authenticated_user}")
            if authenticated_user is None:
                return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
            if not user.is_approved and user.user_type == 3:
                return Response(
                    {'detail': 'Not yet approved, please contact the Alumni Relations Office'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Check if user is blocked
            if not user.is_active:
                return Response(
                    {'detail': 'Your account has been blocked. Please contact the administrator.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Update user status to online when logging in
            # Update user's last_login field
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])
            
            # Set user online in both Redis cache and database
            set_user_online(user.id)
            
            profile, created = Profile.objects.get_or_create(user=user)
            profile.status = 'online'
            profile.last_seen = timezone.now()
            profile.save()
            
            logger.info(f"User {user.id} status set to online on login")
            
            # Broadcast status change to all connected users
            try:
                channel_layer = get_channel_layer()
                status_payload = {
                    'type': 'status_update',
                    'user_id': user.id,
                    'status': 'online',
                    'last_seen': profile.last_seen.isoformat(),
                    'last_login': user.last_login.isoformat()
                }
                logger.info(f"Broadcasting login status update: {status_payload}")
                
                async_to_sync(channel_layer.group_send)(
                    'status_updates',
                    {
                        'type': 'status_update',
                        'data': status_payload
                    }
                )
            except Exception as e:
                logger.error(f"Failed to broadcast status update on login: {str(e)}")
            
            profile.status = 'online'
            profile.last_seen = timezone.now()
            profile.save()
            
            logger.info(f"User {user.id} status set to online on login with last_login updated")
            
            # Broadcast status change to all connected users
            try:
                channel_layer = get_channel_layer()
                status_payload = {
                    'type': 'status_update',
                    'user_id': user.id,
                    'status': 'online',
                    'last_seen': profile.last_seen.isoformat(),
                    'last_login': user.last_login.isoformat()
                }
                logger.info(f"Broadcasting login status update: {status_payload}")
                
                # Broadcast to all users who might have this user in their conversation list
                async_to_sync(channel_layer.group_send)(
                    'user_management',  # User management group
                    {
                        'type': 'broadcast_message',
                        'message': status_payload
                    }
                )
                # Also broadcast to status updates group for backward compatibility
                async_to_sync(channel_layer.group_send)(
                    'status_updates',  # Global status updates group
                    status_payload
                )
                logger.info(f"Successfully broadcast login status update for user {user.id}")
            except Exception as ws_error:
                logger.error(f"WebSocket status broadcast failed in LoginView: {str(ws_error)}")
            
            refresh = RefreshToken.for_user(user)
            return Response({
                'token': str(refresh.access_token),
                'user': UserDetailSerializer(user).data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Login failed for email {email}: {str(e)}", exc_info=True)
            return Response({'detail': 'An error occurred during login.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BlockUserView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def post(self, request, user_id):
        try:
            user = CustomUser.objects.get(id=user_id)
            user.is_active = False
            user.save()
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'admin_notifications',
                {
                    'type': 'notification',
                    'message': f'User {user.email} has been blocked.',
                }
            )
            async_to_sync(channel_layer.group_send)(
                f'user_{user.id}',
                {
                    'type': 'notification',
                    'message': 'Your account has been blocked.',
                }
            )
            cache.delete('approved_alumni_list')
            return Response({'message': 'User blocked successfully'}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

class UnblockUserView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def post(self, request, user_id):
        try:
            user = CustomUser.objects.get(id=user_id)
            user.is_active = True
            user.save()
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'admin_notifications',
                {
                    'type': 'notification',
                    'message': f'User {user.email} has been unblocked.',
                }
            )
            async_to_sync(channel_layer.group_send)(
                f'user_{user.id}',
                {
                    'type': 'notification',
                    'message': 'Your account has been unblocked.',
                }
            )
            cache.delete('approved_alumni_list')
            return Response({'message': 'User unblocked successfully'}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class SkillListCreateView(ListCreateAPIView):
    serializer_class = SkillSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        cache_key = 'skills_list'
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
        queryset = list(Skill.objects.all())
        cache.set(cache_key, queryset, timeout=3600)
        return queryset

class WorkHistoryListCreateView(ListCreateAPIView):
    serializer_class = WorkHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        cache_key = f'work_history_{self.request.user.id}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
        queryset = WorkHistory.objects.filter(user=self.request.user)
        cache.set(cache_key, list(queryset), timeout=3600)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        cache.delete(f'work_history_{self.request.user.id}')

class WorkHistoryDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = WorkHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return WorkHistory.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.user != self.request.user:
            raise PermissionDenied("You can only update your own work history.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied("You can only delete your own work history.")
        instance.delete()

class UserCreateView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def post(self, request):
        serializer = UserCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.save()
            if user.user_type == 3 and not user.is_approved:
                token = generate_token(user)
                confirm_url = request.build_absolute_uri(reverse('confirm_token', kwargs={'token': token}))
                send_mail(
                    subject='Account Created',
                    message=f'Your account was created. Please confirm your email: {confirm_url}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
            return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cache_key = f'user_detail_{request.user.id}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        serializer = UserDetailSerializer(request.user)
        cache.set(cache_key, serializer.data, timeout=3600)
        return Response(serializer.data)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Update user status to offline when logging out
            user = request.user
            
            # Set user offline in both Redis cache and database
            set_user_offline(user.id)
            
            profile, created = Profile.objects.get_or_create(user=user)
            profile.status = 'offline'
            profile.last_seen = timezone.now()
            profile.save()
            
            logger.info(f"User {user.id} status set to offline on logout")
            
            # Clear all active connections for this user
            from messaging_app.consumers import ACTIVE_CONNECTIONS
            if user.id in ACTIVE_CONNECTIONS:
                del ACTIVE_CONNECTIONS[user.id]
                logger.info(f"Cleared all active connections for user {user.id}")
            
            # Broadcast status change to all connected users
            try:
                channel_layer = get_channel_layer()
                status_payload = {
                    'type': 'status_update',
                    'user_id': user.id,
                    'status': 'offline',
                    'last_seen': profile.last_seen.isoformat()
                }
                logger.info(f"Broadcasting logout status update: {status_payload}")
                
                async_to_sync(channel_layer.group_send)(
                    'status_updates',
                    {
                        'type': 'status_update',
                        'data': status_payload
                    }
                )
            except Exception as e:
                logger.error(f"Failed to broadcast status update on logout: {str(e)}")
            
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logged out successfully"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            logger.error(f"Logout failed: {str(e)}")
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)

class PendingAlumniListView(ListAPIView):
    serializer_class = UserDetailSerializer
    permission_classes = [IsAdminOrSuperAdmin]
    pagination_class = None 

    def get_queryset(self):
        return CustomUser.objects.filter(user_type=3, is_approved=False)
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        cache_key = f"user_profile_{user.id}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        serializer = ProfileSerializer(user)
        data = serializer.data
        cache.set(cache_key, data, timeout=300)
        return Response(data)

    def put(self, request):
        user = request.user
        serializer = ProfileSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            cache_key = f"user_profile_{user.id}"
            cache.set(cache_key, serializer.data, timeout=300)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        user = request.user
        serializer = ProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            cache_key = f"user_profile_{user.id}"
            cache.set(cache_key, serializer.data, timeout=300)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
CustomUser = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSearchSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.query_params.get('q', None)
        if search_query:
            queryset = queryset.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(username__icontains=search_query)
            ).exclude(id=self.request.user.id)
        return queryset

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        Only allow admins and super admins to delete users.
        """
        if self.action == 'destroy':
            # Custom permission check for delete - must be Admin or SuperAdmin
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def destroy(self, request, *args, **kwargs):
        """
        Custom delete method for user deletion with additional checks
        """
        instance = self.get_object()
        
        # Check if user has permission to delete (Admin=2 or SuperAdmin=1)
        if request.user.user_type not in [1, 2]:
            return Response(
                {"error": "You don't have permission to delete users"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Prevent users from deleting themselves
        if instance == request.user:
            return Response(
                {"error": "You cannot delete your own account"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Prevent deletion of super admin by regular admin
        # user_type: 1=Super Admin, 2=Admin, 3=Alumni
        if instance.user_type == 1 and request.user.user_type != 1:
            return Response(
                {"error": "Only super admins can delete other super admin accounts"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Clear any cached data related to this user
        cache_keys_to_clear = [
            f"user_approval_count",
            f"pending_users_list",
            f"approved_users_list",
            f"user_status_{instance.id}",
            f"user_profile_{instance.id}",
        ]
        
        for key in cache_keys_to_clear:
            cache.delete(key)
        
        # Also clear pattern-based cache keys
        cache_patterns = [
            "user_*",
            "approval_*",
            "pending_*",
            "approved_*"
        ]
        
        for pattern in cache_patterns:
            cache_keys = cache.keys(pattern)
            if cache_keys:
                cache.delete_many(cache_keys)
        
        # Broadcast the user deletion to WebSocket
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        
        channel_layer = get_channel_layer()
        if channel_layer:
            try:
                async_to_sync(channel_layer.group_send)(
                    "admin_notifications",
                    {
                        "type": "user_deleted",
                        "user_id": instance.id,
                        "user_name": f"{instance.first_name} {instance.last_name}",
                        "deleted_by": f"{request.user.first_name} {request.user.last_name}"
                    }
                )
            except Exception as e:
                print(f"Error broadcasting user deletion: {e}")
        
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

class UserUpdateView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def put(self, request, user_id):
        try:
            user = CustomUser.objects.get(id=user_id)
            serializer = UserDetailSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                cache.delete(f'user_detail_{user.id}')
                cache.delete('approved_alumni_list')
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TestStatusBroadcastView(APIView):
    """Test endpoint to manually broadcast status updates"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            from .models import Profile
            from django.utils import timezone
            from asgiref.sync import async_to_sync
            from channels.layers import get_channel_layer
            
            user = request.user
            test_status = request.data.get('status', 'offline')
            
            # Update user status
            profile, created = Profile.objects.get_or_create(user=user)
            profile.status = test_status
            profile.last_seen = timezone.now()
            profile.save()
            
            # Broadcast status change
            channel_layer = get_channel_layer()
            status_payload = {
                'type': 'status_update',
                'user_id': user.id,
                'status': test_status,
                'last_seen': profile.last_seen.isoformat()
            }
            
            logger.info(f"Test broadcasting status update: {status_payload}")
            
            async_to_sync(channel_layer.group_send)(
                'status_updates',
                status_payload
            )
            
            return Response({
                'message': f'Status broadcast test successful for user {user.id}',
                'payload': status_payload
            })
            
        except Exception as e:
            logger.error(f"Test status broadcast failed: {str(e)}")
            return Response(
                {'error': f'Test failed: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# =============================================================================
# ALUMNI DIRECTORY CRUD VIEWS - For SuperAdmin Management
# =============================================================================

class AlumniDirectoryListCreateView(ListCreateAPIView):
    """
    List all alumni directory entries and create new ones.
    SuperAdmin only access.
    """
    serializer_class = AlumniDirectorySerializer
    permission_classes = [IsAdminOrSuperAdmin]
    
    def get_queryset(self):
        return AlumniDirectory.objects.all().order_by('last_name', 'first_name')
    
    def perform_create(self, serializer):
        serializer.save()


class AlumniDirectoryDetailView(RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete an alumni directory entry.
    SuperAdmin only access.
    """
    serializer_class = AlumniDirectorySerializer
    permission_classes = [IsAdminOrSuperAdmin]
    queryset = AlumniDirectory.objects.all()
    lookup_field = 'id'


class AlumniDirectoryImportView(APIView):
    """
    Import alumni data from CSV, Excel, or Text file.
    SuperAdmin only access.
    """
    permission_classes = [IsAdminOrSuperAdmin]
    
    def post(self, request):
        try:
            file = request.FILES.get('file')
            if not file:
                return Response(
                    {'error': 'No file provided'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check file size (max 10MB)
            if file.size > 10 * 1024 * 1024:
                return Response(
                    {'error': 'File size too large (max 10MB)'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Read file based on extension
            file_name = file.name.lower()
            
            try:
                if file_name.endswith('.csv'):
                    df = pd.read_csv(io.BytesIO(file.read()))
                elif file_name.endswith(('.xlsx', '.xls')):
                    df = pd.read_excel(io.BytesIO(file.read()))
                elif file_name.endswith('.txt'):
                    content = file.read().decode('utf-8')
                    # Assume tab-separated values for text files
                    df = pd.read_csv(io.StringIO(content), sep='\t')
                else:
                    return Response(
                        {'error': 'Unsupported file format. Please use CSV, Excel, or TXT files.'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except Exception as e:
                return Response(
                    {'error': f'Error reading file: {str(e)}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate required columns
            required_columns = ['first_name', 'last_name', 'birth_date', 'program', 'year_graduated', 'sex']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                return Response(
                    {'error': f'Missing required columns: {", ".join(missing_columns)}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Process data
            success_count = 0
            error_count = 0
            errors = []
            
            # Valid programs (from your model)
            valid_programs = [
                'BA in Sociology',
                'Bachelor of Agricultural Technology',
                'Bachelor of Elementary Education',
                'Bachelor of Secondary Education Major in English',
                'Bachelor of Secondary Education Major in Filipino',
                'Bachelor of Secondary Education Major in Mathematics',
                'Bachelor of Secondary Education Major in Science',
                'BS in Agroforestry',
                'BS in Agricultural and Biosystems Engineering',
                'BS in Agriculture',
                'BS in Agriculture, Major in Agribusiness Management',
                'BS in Agriculture, Major in Agricultural Economics',
                'BS in Agriculture, Major in Agronomy',
                'BS in Agriculture, Major in Animal Science',
                'BS in Agriculture, Major in Crop Protection',
                'BS in Agriculture, Major in Horticulture',
                'BS in Agriculture, Major in Soil Science',
                'BS in Applied Mathematics',
                'BS in Biology',
                'BS in Chemistry',
                'BS in Civil Engineering',
                'BS in Computer Science',
                'BS in Electronics Engineering',
                'BS in Environmental Science',
                'BS in Forestry',
                'BS in Geodetic Engineering',
                'BS in Geology',
                'BS in Information Systems',
                'BS in Information Technology',
                'BS in Mathematics',
                'BS in Mining Engineering',
                'BS in Physics',
                'BS in Psychology',
                'BS in Social Work'
            ]
            
            with transaction.atomic():
                for index, row in df.iterrows():
                    try:
                        # Clean and validate data
                        first_name = str(row['first_name']).strip()
                        middle_name = str(row.get('middle_name', '')).strip() if pd.notna(row.get('middle_name', '')) else ''
                        last_name = str(row['last_name']).strip()
                        program = str(row['program']).strip()
                        sex = str(row['sex']).strip().lower()
                        
                        # Validate required fields
                        if not first_name or not last_name:
                            errors.append(f'Row {index + 2}: Missing required fields')
                            error_count += 1
                            continue
                        
                        # Validate program
                        if program not in valid_programs:
                            errors.append(f'Row {index + 2}: Invalid program "{program}"')
                            error_count += 1
                            continue
                        
                        # Validate sex
                        if sex not in ['male', 'female', 'prefer_not_to_say']:
                            errors.append(f'Row {index + 2}: Sex must be male, female, or prefer_not_to_say')
                            error_count += 1
                            continue
                        
                        # Parse birth_date
                        try:
                            if pd.notna(row['birth_date']):
                                birth_date = pd.to_datetime(row['birth_date']).date()
                            else:
                                errors.append(f'Row {index + 2}: Birth date is required')
                                error_count += 1
                                continue
                        except:
                            errors.append(f'Row {index + 2}: Invalid birth date format')
                            error_count += 1
                            continue
                        
                        # Parse year_graduated
                        try:
                            year_graduated = int(row['year_graduated'])
                            if year_graduated < 1900 or year_graduated > 2030:
                                errors.append(f'Row {index + 2}: Year graduated must be between 1900 and 2030')
                                error_count += 1
                                continue
                        except:
                            errors.append(f'Row {index + 2}: Invalid year graduated')
                            error_count += 1
                            continue
                        
                        # Check for duplicates by combination of fields (since school_id is removed)
                        if AlumniDirectory.objects.filter(
                            first_name__iexact=first_name,
                            last_name__iexact=last_name,
                            birth_date=birth_date,
                            program__iexact=program,
                            year_graduated=year_graduated
                        ).exists():
                            errors.append(f'Row {index + 2}: Alumni record with same details already exists')
                            error_count += 1
                            continue
                        
                        # Create alumni record
                        AlumniDirectory.objects.create(
                            first_name=first_name,
                            middle_name=middle_name,
                            last_name=last_name,
                            birth_date=birth_date,
                            program=program,
                            year_graduated=year_graduated,
                            sex=sex
                        )
                        
                        success_count += 1
                        
                    except Exception as e:
                        errors.append(f'Row {index + 2}: {str(e)}')
                        error_count += 1
            
            return Response({
                'message': 'Import completed',
                'success_count': success_count,
                'error_count': error_count,
                'errors': errors[:10],  # Limit to first 10 errors
                'total_errors': len(errors)
            })
            
        except Exception as e:
            logger.error(f"Alumni import error: {str(e)}")
            return Response(
                {'error': f'Import failed: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# LinkedIn-style Social Feature Views
class EnhancedProfileView(APIView):
    """Enhanced Profile view with LinkedIn-style features"""
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id=None, username=None):
        # Handle different lookup methods
        if username:
            # Lookup by username
            try:
                user = CustomUser.objects.get(username=username, is_approved=True, is_active=True)
            except CustomUser.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        elif user_id:
            # Lookup by ID (legacy support)
            try:
                user = CustomUser.objects.get(id=user_id)
            except CustomUser.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Current user's profile
            user = request.user

        # Get or create profile
        from .models import Profile
        profile, created = Profile.objects.get_or_create(user=user)
        
        # Use enhanced serializer with social features
        from .serializers import EnhancedUserDetailSerializer
        serializer = EnhancedUserDetailSerializer(user, context={'request': request})
        return Response(serializer.data)

    def patch(self, request):
        """Update current user's profile"""
        user = request.user
        from .models import Profile
        profile, created = Profile.objects.get_or_create(user=user)
        
        # Update profile fields
        profile_data = {}
        updatable_fields = [
            'bio', 'headline', 'location', 'summary', 'linkedin_url', 'facebook_url', 
            'twitter_url', 'instagram_url', 'website_url', 'profile_visibility', 
            'allow_contact', 'allow_messaging'
        ]
        
        for field in updatable_fields:
            if field in request.data:
                profile_data[field] = request.data[field]
        
        # Handle cover photo upload
        if 'cover_photo' in request.FILES:
            profile_data['cover_photo'] = request.FILES['cover_photo']
        
        # Update profile
        for field, value in profile_data.items():
            setattr(profile, field, value)
        profile.save()
        
        # Clear cache
        cache_key = f"user_profile_{user.id}"
        cache.delete(cache_key)
        
        # Return updated profile
        from .serializers import EnhancedUserDetailSerializer
        serializer = EnhancedUserDetailSerializer(user, context={'request': request})
        return Response(serializer.data)


class FollowUserView(APIView):
    """Follow/Unfollow a user"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, user_id):
        """Send connection invitation to a user (LinkedIn-style)"""
        try:
            target_user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if target_user == request.user:
            return Response({'error': 'Cannot connect to yourself'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if already connected or has pending request
        from .models import Following
        existing_connection = Following.objects.filter(
            follower=request.user,
            following=target_user
        ).first()
        
        if existing_connection:
            if existing_connection.status == 'pending':
                return Response({'message': 'Connection request already sent'}, status=status.HTTP_200_OK)
            elif existing_connection.status == 'accepted':
                return Response({'message': 'Already connected to this user'}, status=status.HTTP_200_OK)
        
        # Create pending connection request (LinkedIn-style)
        following = Following.objects.create(
            follower=request.user,
            following=target_user,
            status='pending'
        )
        
        return Response({
            'message': 'Connection request sent successfully',
            'status': 'pending'
        }, status=status.HTTP_201_CREATED)
    
    def delete(self, request, user_id):
        """Disconnect from a user (removes mutual connection)"""
        try:
            target_user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            from .models import Following
            # Remove the connection from current user to target user
            following = Following.objects.get(follower=request.user, following=target_user)
            following.delete()
            
            # Remove the reverse connection (mutual disconnection)
            reverse_following = Following.objects.filter(
                follower=target_user, 
                following=request.user
            ).first()
            if reverse_following:
                reverse_following.delete()
            
            return Response({'message': 'Successfully disconnected from user'}, status=status.HTTP_200_OK)
        except Following.DoesNotExist:
            return Response({'error': 'Not connected to this user'}, status=status.HTTP_400_BAD_REQUEST)


class UserConnectionsView(APIView):
    """Get user's connections (followers/following)"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, user_id=None):
        # If user_id is provided, get that user's connections; otherwise get current user's connections
        if user_id:
            try:
                user = CustomUser.objects.get(id=user_id)
            except CustomUser.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            user = request.user
        
        connection_type = request.query_params.get('type', 'all')  # 'followers', 'following', 'mutual', 'all', 'invitations'
        
        from .models import Following
        from .serializers import FollowingSerializer
        
        if connection_type == 'followers':
            connections = Following.objects.filter(following=user, status='accepted').select_related('follower')
            serializer = FollowingSerializer(connections, many=True, context={'request': request})
        elif connection_type == 'following':
            connections = Following.objects.filter(follower=user, status='accepted').select_related('following')
            serializer = FollowingSerializer(connections, many=True, context={'request': request})
        elif connection_type == 'mutual':
            connections = Following.objects.filter(
                following=user, is_mutual=True, status='accepted'
            ).select_related('follower')
            serializer = FollowingSerializer(connections, many=True, context={'request': request})
        elif connection_type == 'invitations':
            # Get pending invitations sent TO the current user
            invitations = Following.objects.filter(
                following=user, status='pending'
            ).select_related('follower')
            serializer = FollowingSerializer(invitations, many=True, context={'request': request})
            return Response(serializer.data)
        else:  # all
            followers = Following.objects.filter(following=user, status='accepted').select_related('follower')
            following = Following.objects.filter(follower=user, status='accepted').select_related('following')
            invitations = Following.objects.filter(following=user, status='pending').select_related('follower')
            
            return Response({
                'followers': FollowingSerializer(followers, many=True, context={'request': request}).data,
                'following': FollowingSerializer(following, many=True, context={'request': request}).data,
                'invitations': FollowingSerializer(invitations, many=True, context={'request': request}).data,
                'followers_count': followers.count(),
                'following_count': following.count(),
                'mutual_count': Following.objects.filter(following=user, is_mutual=True, status='accepted').count(),
                'invitations_count': invitations.count()
            })
        
        return Response(serializer.data)


class InvitationManageView(APIView):
    """Accept or reject connection invitations"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, invitation_id):
        """Accept a connection invitation"""
        try:
            from .models import Following
            invitation = Following.objects.get(
                id=invitation_id,
                following=request.user,  # Invitation sent TO current user
                status='pending'
            )
            
            # Accept the invitation
            invitation.status = 'accepted'
            invitation.save()
            
            return Response({
                'message': f'Connection accepted with {invitation.follower.first_name} {invitation.follower.last_name}!',
                'status': 'accepted'
            }, status=status.HTTP_200_OK)
            
        except Following.DoesNotExist:
            return Response({'error': 'Invitation not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error accepting invitation {invitation_id}: {str(e)}")
            return Response({'error': 'Failed to accept invitation'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request, invitation_id):
        """Reject/ignore a connection invitation"""
        try:
            from .models import Following
            invitation = Following.objects.get(
                id=invitation_id,
                following=request.user,  # Invitation sent TO current user
                status='pending'
            )
            
            # Delete the invitation (reject it)
            sender_name = f"{invitation.follower.first_name} {invitation.follower.last_name}"
            invitation.delete()
            
            return Response({
                'message': f'Connection request from {sender_name} has been ignored.',
                'status': 'rejected'
            }, status=status.HTTP_200_OK)
            
        except Following.DoesNotExist:
            return Response({'error': 'Invitation not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error rejecting invitation {invitation_id}: {str(e)}")
            return Response({'error': 'Failed to reject invitation'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class InvitationAcceptView(APIView):
    """Accept connection invitations"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, invitation_id):
        """Accept a connection invitation"""
        try:
            from .models import Following
            invitation = Following.objects.get(
                id=invitation_id,
                following=request.user,  # Invitation sent TO current user
                status='pending'
            )
            
            # Accept the invitation
            invitation.status = 'accepted'
            invitation.save()
            
            return Response({
                'message': f'Connection accepted with {invitation.follower.first_name} {invitation.follower.last_name}!',
                'status': 'accepted'
            }, status=status.HTTP_200_OK)
            
        except Following.DoesNotExist:
            return Response({'error': 'Invitation not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error accepting invitation {invitation_id}: {str(e)}")
            return Response({'error': 'Failed to accept invitation'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class InvitationRejectView(APIView):
    """Reject connection invitations"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, invitation_id):
        """Reject/ignore a connection invitation"""
        try:
            from .models import Following
            invitation = Following.objects.get(
                id=invitation_id,
                following=request.user,  # Invitation sent TO current user
                status='pending'
            )
            
            # Delete the invitation (reject it)
            sender_name = f"{invitation.follower.first_name} {invitation.follower.last_name}"
            invitation.delete()
            
            return Response({
                'message': f'Connection request from {sender_name} has been ignored.',
                'status': 'rejected'
            }, status=status.HTTP_200_OK)
            
        except Following.DoesNotExist:
            return Response({'error': 'Invitation not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error rejecting invitation {invitation_id}: {str(e)}")
            return Response({'error': 'Failed to reject invitation'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AchievementListCreateView(ListCreateAPIView):
    """List and create achievements for authenticated user"""
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        from .serializers import AchievementSerializer
        return AchievementSerializer
    
    def get_queryset(self):
        from .models import Achievement
        user_id = self.kwargs.get('user_id')
        if user_id:
            return Achievement.objects.filter(user_id=user_id)
        return Achievement.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AchievementDetailView(RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete an achievement"""
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        from .serializers import AchievementSerializer
        return AchievementSerializer
    
    def get_queryset(self):
        from .models import Achievement
        return Achievement.objects.filter(user=self.request.user)


class EducationListCreateView(ListCreateAPIView):
    """List and create education entries for authenticated user"""
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        from .serializers import EducationSerializer
        return EducationSerializer
    
    def get_queryset(self):
        from .models import Education
        user_id = self.kwargs.get('user_id')
        if user_id:
            return Education.objects.filter(user_id=user_id)
        return Education.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class EducationDetailView(RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete an education entry"""
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        from .serializers import EducationSerializer
        return EducationSerializer
    
    def get_queryset(self):
        from .models import Education
        return Education.objects.filter(user=self.request.user)


class ProfileSearchView(APIView):
    """Search for alumni profiles"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        query = request.query_params.get('q', '')
        program = request.query_params.get('program', '')
        year_graduated = request.query_params.get('year_graduated', '')
        employment_status = request.query_params.get('employment_status', '')
        location = request.query_params.get('location', '')
        
        # Base queryset - only approved alumni
        queryset = CustomUser.objects.filter(
            user_type=3,  # Alumni only
            is_approved=True
        ).select_related('profile')
        
        # Apply filters
        if query:
            queryset = queryset.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(profile__headline__icontains=query) |
                Q(profile__summary__icontains=query) |
                Q(profile__present_occupation__icontains=query) |
                Q(profile__employing_agency__icontains=query)
            )
        
        if program:
            queryset = queryset.filter(program__icontains=program)
        
        if year_graduated:
            queryset = queryset.filter(year_graduated=year_graduated)
        
        if employment_status:
            queryset = queryset.filter(employment_status=employment_status)
        
        if location:
            queryset = queryset.filter(profile__location__icontains=location)
        
        # Exclude current user
        queryset = queryset.exclude(id=request.user.id)
        
        # Paginate results
        from rest_framework.pagination import PageNumberPagination
        paginator = PageNumberPagination()
        paginator.page_size = 20
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        
        from .serializers import EnhancedUserDetailSerializer
        serializer = EnhancedUserDetailSerializer(
            paginated_queryset, 
            many=True, 
            context={'request': request}
        )
        
        return paginator.get_paginated_response(serializer.data)


class SuggestedConnectionsView(APIView):
    """Get suggested connections for the current user"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Get users that current user is not following
        from .models import Following
        following_ids = Following.objects.filter(follower=user).values_list('following_id', flat=True)
        
        # Get suggested connections based on:
        # 1. Same program
        # 2. Same year graduated
        # 3. Same employment status
        # 4. Mutual connections
        suggestions = CustomUser.objects.filter(
            user_type=3,  # Alumni only
            is_approved=True,
            is_active=True
        ).exclude(
            Q(id=user.id) |  # Exclude self
            Q(id__in=following_ids)  # Exclude already following
        ).select_related('profile')
        
        # Prioritize by same program and year
        same_program = suggestions.filter(program=user.program)
        same_year = suggestions.filter(year_graduated=user.year_graduated)
        
        # Combine and limit results
        final_suggestions = list(same_program[:5]) + list(same_year[:5])
        
        # Remove duplicates and limit to 10
        seen = set()
        unique_suggestions = []
        for suggestion in final_suggestions:
            if suggestion.id not in seen:
                unique_suggestions.append(suggestion)
                seen.add(suggestion.id)
                if len(unique_suggestions) >= 10:
                    break
        
        # If we need more suggestions, add random approved alumni
        if len(unique_suggestions) < 10:
            additional = suggestions.exclude(
                id__in=[s.id for s in unique_suggestions]
            ).order_by('?')[:10 - len(unique_suggestions)]
            unique_suggestions.extend(additional)
        
        from .serializers import EnhancedUserDetailSerializer
        serializer = EnhancedUserDetailSerializer(
            unique_suggestions, 
            many=True, 
            context={'request': request}
        )
        
        return Response(serializer.data)


class UserByNameView(APIView):
    """
    Resolve a user by their name (first_name + last_name) to get user ID and basic info.
    Used for name-based URL routing.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, user_name):
        try:
            # Get all approved and active users
            users = CustomUser.objects.filter(is_approved=True, is_active=True)
            
            # Check each user to find a match
            for user in users:
                # Create name identifier from first_name + last_name
                full_name_no_space = (user.first_name + user.last_name).lower().replace(' ', '')
                
                # Check for exact match
                if full_name_no_space == user_name.lower():
                    return Response({
                        'id': user.id,
                        'username': user.username,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'full_name': f"{user.first_name} {user.last_name}".strip()
                    })
            
            # If no exact match found, also try username match
            user_by_username = users.filter(username__iexact=user_name).first()
            if user_by_username:
                return Response({
                    'id': user_by_username.id,
                    'username': user_by_username.username,
                    'first_name': user_by_username.first_name,
                    'last_name': user_by_username.last_name,
                    'full_name': f"{user_by_username.first_name} {user_by_username.last_name}".strip()
                })
            
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
            
        except Exception as e:
            return Response(
                {'error': 'Error resolving user name'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdminAnalyticsView(APIView):
    """
    Provide comprehensive analytics data for the admin dashboard
    """
    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request):
        try:
            from datetime import timedelta
            from django.utils import timezone
            from django.db.models import Count
            
            # Try to import posts app models
            try:
                from posts_app.models import Post, PostReport
                posts_available = True
            except ImportError:
                posts_available = False
                logger.warning("Posts app not available for analytics")
            
            # Get current date
            today = timezone.now().date()
            week_ago = today - timedelta(days=7)
            
            # User analytics
            total_users = CustomUser.objects.count()
            active_users = CustomUser.objects.filter(is_active=True).count()
            pending_approvals = CustomUser.objects.filter(
                user_type=3, 
                is_approved=False
            ).count()
            
            # Recent registrations (last 7 days)
            # Count only approved alumni registered in the last 7 days
            recent_registrations = CustomUser.objects.filter(
                date_joined__date__gte=week_ago,
                user_type=3,
                is_approved=True
            ).count()
            
            # Online users (users active in last 15 minutes)
            fifteen_minutes_ago = timezone.now() - timedelta(minutes=15)
            online_users = CustomUser.objects.filter(
                last_login__gte=fifteen_minutes_ago
            ).count()
            
            # Initialize default post analytics
            posts_analytics = {
                'total': 0,
                'pending': 0,
                'approved': 0,
                'declined': 0,
                'reported': 0,
                'weekly_posts': 0,
                'approval_rate': 0,
                'by_status': []
            }
            
            reports_analytics = {
                'pending': 0,
                'total': 0,
                'resolved_today': 0
            }
            
            # Post analytics (if posts app is available)
            if posts_available:
                try:
                    total_posts = Post.objects.count()
                    pending_posts = Post.objects.filter(status='pending').count()
                    approved_posts = Post.objects.filter(status='approved').count()
                    declined_posts = Post.objects.filter(status='declined').count()
                    
                    # Reported posts analytics
                    reported_posts = PostReport.objects.filter(is_resolved=False).count()
                    
                    # Posts by status breakdown
                    posts_by_status = Post.objects.values('status').annotate(
                        count=Count('id')
                    )
                    
                    # Weekly activity
                    weekly_posts = Post.objects.filter(
                        created_at__date__gte=week_ago
                    ).count()
                    
                    # Approval rate
                    total_reviewed = approved_posts + declined_posts
                    approval_rate = (approved_posts / total_reviewed * 100) if total_reviewed > 0 else 0
                    
                    posts_analytics.update({
                        'total': total_posts,
                        'pending': pending_posts,
                        'approved': approved_posts,
                        'declined': declined_posts,
                        'reported': reported_posts,
                        'weekly_posts': weekly_posts,
                        'approval_rate': round(approval_rate, 2),
                        'by_status': list(posts_by_status)
                    })
                    
                    reports_analytics.update({
                        'pending': reported_posts,
                        'total': PostReport.objects.count(),
                        'resolved_today': PostReport.objects.filter(
                            is_resolved=True,
                            resolved_at__date=today
                        ).count()
                    })
                    
                except Exception as e:
                    logger.warning(f"Posts analytics failed: {str(e)}")
            
            analytics_data = {
                'users': {
                    'total': total_users,
                    'active': active_users,
                    'pending_approvals': pending_approvals,
                    'recent_registrations': recent_registrations,
                    'online_now': online_users,
                    'activity_rate': round((active_users / total_users * 100), 2) if total_users > 0 else 0
                },
                'posts': posts_analytics,
                'reports': reports_analytics,
                'summary': {
                    'pending_actions': reports_analytics['pending'] + pending_approvals,
                    'total_content': posts_analytics['total'],
                    'user_engagement': round((online_users / active_users * 100), 2) if active_users > 0 else 0
                },
                'last_updated': timezone.now().isoformat()
            }
            
            return Response(analytics_data)
            
        except Exception as e:
            logger.error(f"Analytics data fetch failed: {str(e)}")
            return Response(
                {'error': 'Failed to fetch analytics data'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )