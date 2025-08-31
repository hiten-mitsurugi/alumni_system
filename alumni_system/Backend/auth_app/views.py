from aiohttp import request
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
from .models import CustomUser, Skill, WorkHistory, SurveyCategory, SurveyQuestion, SurveyResponse
from .serializers import (
    RegisterSerializer, UserDetailSerializer, UserCreateSerializer,
    SkillSerializer, WorkHistorySerializer, AlumniDirectoryCheckSerializer,
    SurveyCategorySerializer, SurveyQuestionSerializer, SurveyResponseSerializer, SurveyResponseCreateSerializer
)
from .permissions import IsAdminOrSuperAdmin
from .utils import generate_token, confirm_token
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
import logging


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
    """
    Returns a filtered, cached, and paginated list of approved alumni users.
    Applies filters for employment status, graduation year, program, gender, account status, and search input.
    Caches each unique filter set for performance optimization.
    """
    serializer_class = UserDetailSerializer
    permission_classes = [IsAdminOrSuperAdmin]

    def get_queryset(self):
        request = self.request

        # Get filter parameters
        employment_status = request.query_params.get('employment_status', '').strip().lower()
        gender = request.query_params.get('gender', '').strip().lower()
        year_graduated = request.query_params.get('year_graduated', '').strip()
        program = request.query_params.get('program', '').strip()
        status = request.query_params.get('status', '').strip().lower()
        search = request.query_params.get('search', '').strip()

        # Cache key
        cache_key = f"approved_alumni_list_{employment_status}_{gender}_{year_graduated}_{program}_{status}_{search}"

        cached_ids = cache.get(cache_key)
        if cached_ids is not None:
            return CustomUser.objects.filter(id__in=cached_ids)

        queryset = CustomUser.objects.filter(user_type=3, is_approved=True)

        # Filters
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

        # Cache only the user IDs
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
        
logger = logging.getLogger(__name__)

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

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Extract survey responses from request data
        survey_responses_data = request.data.get('survey_responses', '{}')
        
        # Parse JSON if it's a string
        if isinstance(survey_responses_data, str):
            import json
            try:
                survey_responses_data = json.loads(survey_responses_data)
            except json.JSONDecodeError:
                return Response({'error': 'Invalid survey responses format'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create a copy of request data without survey responses for user creation
        user_data = request.data.copy()
        if 'survey_responses' in user_data:
            del user_data['survey_responses']
        
        # Create user
        serializer = RegisterSerializer(data=user_data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Save survey responses
            if survey_responses_data:
                try:
                    for question_id, response_value in survey_responses_data.items():
                        try:
                            question = SurveyQuestion.objects.get(id=int(question_id))
                            
                            # Handle different response types
                            if isinstance(response_value, list):
                                response_value = response_value  # Keep as list for JSON field
                            
                            SurveyResponse.objects.create(
                                user=user,
                                question=question,
                                response=response_value
                            )
                        except (SurveyQuestion.DoesNotExist, ValueError) as e:
                            logger.warning(f"Invalid question ID {question_id}: {str(e)}")
                            continue
                            
                except Exception as e:
                    logger.error(f"Failed to save survey responses for user {user.id}: {str(e)}")
                    # Don't fail registration if survey saving fails
            
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
            except Exception as e:
                logger.error(f"WebSocket notification failed in RegisterView: {str(e)}")
            
            return Response({'message': 'User registered successfully, pending approval.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

try:
    from django.core.mail import send_mail
    from django.conf import settings
except ImportError as e:
    logging.getLogger(__name__).error(f"Failed to import email modules: {str(e)}", exc_info=True)
    send_mail = None
    settings = None

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        print(f"Login attempt with email: {email}")  # Debug print

        if not email or not password:
            return Response({'detail': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.filter(email=email).first()
            if user is None:
                print(f"No user found with email: {email}")  # Debug print
                return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

            print(f"Found user: {user.username}, active: {user.is_active}, password: {user.password[:20]}...")  # Debug print

            # Use email for authentication
            authenticated_user = authenticate(request=request, email=email, password=password)
            print(f"Authentication result: {authenticated_user}")  # Debug print

            if authenticated_user is None:
                print("Authentication failed")  # Debug print
                return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

            # Generate JWT tokens
            refresh = RefreshToken.for_user(authenticated_user)
            access_token = refresh.access_token

            # Return user info and tokens
            return Response({
                'token': str(access_token),
                'refresh': str(refresh),
                'user': {
                    'id': authenticated_user.id,
                    'email': authenticated_user.email,
                    'username': authenticated_user.username,
                    'first_name': authenticated_user.first_name,
                    'last_name': authenticated_user.last_name,
                    'user_type': authenticated_user.user_type,
                    'is_superuser': authenticated_user.is_superuser,
                    'is_staff': authenticated_user.is_staff,
                    'is_approved': authenticated_user.is_approved,
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            # Add proper exception handling
            print(f"Login error: {str(e)}")
            return Response({'detail': 'An error occurred during login'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BlockUserView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def post(self, request, user_id):
        try:
            user = CustomUser.objects.get(id=user_id)
            user.is_active = False
            user.save()
            try:
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
            except Exception as e:
                logger.warning(f"WebSocket notification failed for user {user.id}: {str(e)}")
            cache.delete('approved_alumni_list')
            return Response({'message': 'User blocked successfully'}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error in BlockUserView for user_id {user_id}: {str(e)}")
            return Response({'error': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UnblockUserView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def post(self, request, user_id):
        try:
            user = CustomUser.objects.get(id=user_id)
            user.is_active = True
            user.save()
            try:
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
            except Exception as e:
                logger.warning(f"WebSocket notification failed for user {user.id}: {str(e)}")
            cache.delete('approved_alumni_list')
            return Response({'message': 'User unblocked successfully'}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error in UnblockUserView for user_id {user_id}: {str(e)}")
            return Response({'error': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
        try:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'admin_notifications',
                {
                    'type': 'notification',
                    'message': f'New work history added by {self.request.user.email}',
                }
            )
        except Exception as e:
            logger.warning(f"WebSocket notification failed for work history: {str(e)}")
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

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        cache_key = f"user_profile_{user.id}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        serializer = UserDetailSerializer(user)
        cache.set(cache_key, serializer.data, timeout=300)
        return Response(serializer.data)
    
    def put(self, request):
        print(f"=== PROFILE UPDATE DEBUG ===")
        print(f"User: {request.user}")
        print(f"User authenticated: {request.user.is_authenticated}")
        print(f"Request data: {request.data}")
        print(f"Request FILES: {request.FILES}")
        
        user = request.user
        serializer = UserDetailSerializer(user, data=request.data, partial=True)
        
        print(f"Serializer is_valid: {serializer.is_valid()}")
        if not serializer.is_valid():
            print(f"Serializer errors: {serializer.errors}")
        
        if serializer.is_valid():
            print("Serializer validation passed")
            
            # Handle profile picture upload
            if 'profile_picture' in request.FILES:
                print(f"Profile picture found: {request.FILES['profile_picture']}")
                user.profile_picture = request.FILES['profile_picture']
            
            # Update other fields
            for field, value in serializer.validated_data.items():
                if field != 'profile_picture':  # Skip profile picture as we handled it above
                    print(f"Updating field {field}: {getattr(user, field)} -> {value}")
                    setattr(user, field, value)
            
            user.save()
            print("User saved successfully")
            
            # Clear cache
            cache.delete(f"user_profile_{user.id}")
            
            # Return updated user data
            updated_serializer = UserDetailSerializer(user)
            print("Returning updated user data")
            return Response(updated_serializer.data, status=status.HTTP_200_OK)
        
        print(f"Returning validation errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserCreateView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def post(self, request):
        serializer = UserCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.save()
            if user.user_type == 3 and not user.is_approved:
                try:
                    token = generate_token(user)
                    confirm_url = request.build_absolute_uri(reverse('confirm_token', kwargs={'token': token}))
                    send_mail(
                        subject='Account Created',
                        message=f'Your account was created. Please confirm your email: {confirm_url}',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        fail_silently=False,
                    )
                except Exception as e:
                    logger.error(f"Failed to send confirmation email to {user.email}: {str(e)}")
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

# Survey Management Views
class SurveyCategoryListCreateView(ListCreateAPIView):
    """List and create survey categories (SuperAdmin only)"""
    queryset = SurveyCategory.objects.all()
    serializer_class = SurveyCategorySerializer
    permission_classes = [IsAdminOrSuperAdmin]

class SurveyCategoryDetailView(RetrieveUpdateDestroyAPIView):
    """Retrieve, update, delete survey categories (SuperAdmin only)"""
    queryset = SurveyCategory.objects.all()
    serializer_class = SurveyCategorySerializer
    permission_classes = [IsAdminOrSuperAdmin]

class SurveyQuestionListCreateView(ListCreateAPIView):
    """List and create survey questions (SuperAdmin only)"""
    queryset = SurveyQuestion.objects.select_related('category').filter(is_active=True)
    serializer_class = SurveyQuestionSerializer
    permission_classes = [IsAdminOrSuperAdmin]

class SurveyQuestionDetailView(RetrieveUpdateDestroyAPIView):
    """Retrieve, update, delete survey questions (SuperAdmin only)"""
    queryset = SurveyQuestion.objects.all()
    serializer_class = SurveyQuestionSerializer
    permission_classes = [IsAdminOrSuperAdmin]

class ActiveSurveyQuestionsView(APIView):
    """Get all active survey questions for registration form"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        categories = SurveyCategory.objects.filter(
            is_active=True
        ).prefetch_related('questions')
        
        survey_data = []
        for category in categories:
            questions = category.questions.filter(is_active=True).order_by('order')
            if questions.exists():
                survey_data.append({
                    'id': category.id,
                    'name': category.name,
                    'order': category.order,
                    'questions': SurveyQuestionSerializer(questions, many=True).data
                })
        
        return Response(survey_data)

class SurveyResponseSubmitView(APIView):
    """Submit survey responses during registration"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = SurveyResponseCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            responses_data = serializer.validated_data['responses']
            user = request.user
            
            # Delete existing responses for this user (in case of re-submission)
            SurveyResponse.objects.filter(user=user).delete()
            
            # Create new responses
            for response_data in responses_data:
                question_id = response_data.get('question_id')
                try:
                    question = SurveyQuestion.objects.get(id=question_id, is_active=True)
                    
                    # Create response based on question type
                    response_obj = SurveyResponse(user=user, question=question)
                    
                    if question.question_type in ['text', 'textarea', 'email']:
                        response_obj.response_text = response_data.get('value', '')
                    elif question.question_type == 'number':
                        response_obj.response_number = response_data.get('value')
                    elif question.question_type == 'date':
                        response_obj.response_date = response_data.get('value')
                    elif question.question_type in ['select', 'radio', 'checkbox', 'rating', 'yes_no']:
                        response_obj.response_json = response_data.get('value')
                    
                    response_obj.save()
                    
                except SurveyQuestion.DoesNotExist:
                    return Response(
                        {'error': f'Question with ID {question_id} not found'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            return Response({'message': 'Survey responses submitted successfully'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserSurveyResponsesView(APIView):
    """Get survey responses for a specific user"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, user_id=None):
        # SuperAdmin can view any user's responses, regular users can only view their own
        if user_id:
            if not (request.user.is_superuser or request.user.user_type == 1):
                return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
            try:
                user = CustomUser.objects.get(id=user_id)
            except CustomUser.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            user = request.user
        
        responses = SurveyResponse.objects.filter(user=user).select_related('question', 'question__category')
        serializer = SurveyResponseSerializer(responses, many=True)
        return Response(serializer.data)
