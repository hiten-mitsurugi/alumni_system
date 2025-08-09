from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import ListAPIView, RetrieveAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.conf import settings
from django.core.cache import cache
from django.db.models import Q
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import transaction
from .models import CustomUser, Skill, WorkHistory
from .serializers import (
    RegisterSerializer, UserDetailSerializer, UserCreateSerializer,
    SkillSerializer, WorkHistorySerializer, AlumniDirectoryCheckSerializer,
    ProfileSerializer, UserSearchSerializer
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
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            try:
                with transaction.atomic():
                    user = serializer.save()

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

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ApproveUserView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def post(self, request, user_id):
        try:
            user = CustomUser.objects.get(id=user_id, user_type=3, is_approved=False)
            user.is_approved = True
            user.save()
            return Response({'message': 'User approved successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

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
        cache_key = f"approved_alumni_list_{employment_status}_{gender}_{year_graduated}_{program}_{status}_{search}"
        cached_ids = cache.get(cache_key)
        if cached_ids is not None:
            return CustomUser.objects.filter(id__in=cached_ids)
        queryset = CustomUser.objects.filter(user_type=3, is_approved=True)
        if employment_status:
            queryset = queryset.filter(employment_status__iexact=employment_status)
        if gender:
            queryset = queryset.filter(gender__iexact=gender)
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
                Q(school_id__icontains=search)
            )
        user_ids = list(queryset.values_list('id', flat=True))
        cache.set(cache_key, user_ids, timeout=3600)
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
            user = CustomUser.objects.get(id=user_id)
            user.delete()
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'user_{user_id}',
                {
                    'type': 'notification',
                    'message': 'Your account was rejected.',
                }
            )
            cache.delete('approved_alumni_list')
            cache.delete('pending_alumni_list')
            return Response({'message': 'User rejected and deleted successfully'})
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        if not email or not password:
            return Response({'detail': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = CustomUser.objects.filter(email=email).first()
            if user is None:
                return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
            authenticated_user = authenticate(request=request, username=email, password=password)
            if authenticated_user is None:
                return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
            if not user.is_approved and user.user_type == 3:
                return Response(
                    {'detail': 'Not yet approved, please contact the Alumni Relations Office'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Update user status to online when logging in
            from .models import Profile
            from django.utils import timezone
            from asgiref.sync import async_to_sync
            from channels.layers import get_channel_layer
            
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
                    'last_seen': profile.last_seen.isoformat()
                }
                logger.info(f"Broadcasting login status update: {status_payload}")
                
                # Broadcast to all users who might have this user in their conversation list
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
            from .models import Profile
            from django.utils import timezone
            from asgiref.sync import async_to_sync
            from channels.layers import get_channel_layer
            
            user = request.user
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
                    'status_updates',  # Global status updates group
                    status_payload
                )
                logger.info(f"Successfully broadcast logout status update for user {user.id}")
            except Exception as ws_error:
                logger.error(f"WebSocket status broadcast failed in LogoutView: {str(ws_error)}")
            
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

class UserViewSet(viewsets.ReadOnlyModelViewSet):
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