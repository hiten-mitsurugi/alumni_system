"""
User Management Views - Approve/Reject/Block/Unblock users, User CRUD operations
"""
from .base_imports import *

class ApproveUserView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def post(self, request, user_id):
        try:
            # Store user data before transaction
            user_data = {}
            
            with transaction.atomic():
                user = CustomUser.objects.get(id=user_id, user_type=3, is_approved=False)
                
                # Store user info for background tasks
                user_data = {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'username': user.username,
                    'year_graduated': user.year_graduated,
                    'program': user.program,
                }
                
                # Approve user
                user.is_approved = True
                user.save()
                
                # Clear only critical caches immediately (fast operation)
                cache.delete('approved_alumni_list')
                cache.delete('pending_alumni_list')
                cache.delete(f'user_detail_{user.id}')
            
            # Send immediate WebSocket notification (fast)
            try:
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    'admin_group',
                    {
                        'type': 'notification',
                        'message': f'User {user_data["first_name"]} {user_data["last_name"]} has been approved.',
                    }
                )
            except Exception as ws_error:
                logger.error(f"WebSocket notification failed: {str(ws_error)}")
            
            # Queue background tasks for slow operations
            try:
                from auth_app.tasks import send_approval_email_task, clear_approval_caches_task
                
                # Send email in background
                send_approval_email_task.delay(
                    user_data['id'],
                    user_data['email'],
                    user_data['first_name'],
                    user_data['last_name'],
                    user_data['username']
                )
                
                # Clear additional caches in background
                clear_approval_caches_task.delay(
                    user_data['id'],
                    user_data['year_graduated'],
                    user_data['program'],
                    user_data['first_name'],
                    user_data['last_name']
                )
                
                logger.info(f"User {user_id} approved - background tasks queued")
                
            except Exception as task_error:
                logger.error(f"Failed to queue background tasks: {str(task_error)}")
                # Don't fail the request - user is still approved
            
            # Return immediately (fast response)
            return Response({
                'message': 'User approved successfully',
                'email_queued': True,
                'user': {
                    'id': user_data['id'],
                    'name': f"{user_data['first_name']} {user_data['last_name']}",
                    'email': user_data['email']
                }
            }, status=status.HTTP_200_OK)
                
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found or already approved'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error approving user {user_id}: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RejectUserView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def post(self, request, user_id):
        try:
            user = CustomUser.objects.get(id=user_id, user_type=3, is_approved=False)
            
            # Store user data before deletion
            user_data = {
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'username': user.username,
            }
            
            # Delete the user account
            user.delete()
            
            # Send immediate WebSocket notification (fast)
            try:
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f'user_{user_id}',
                    {
                        'type': 'notification',
                        'message': 'Your account application requires additional review.',
                    }
                )
            except Exception as ws_error:
                logger.error(f"WebSocket notification failed: {str(ws_error)}")
            
            # Clear caches immediately
            cache.delete('approved_alumni_list')
            cache.delete('pending_alumni_list')
            
            # Queue email sending in background
            try:
                from auth_app.tasks import send_rejection_email_task
                
                send_rejection_email_task.delay(
                    user_data['email'],
                    user_data['first_name'],
                    user_data['last_name'],
                    user_data['username']
                )
                
                logger.info(f"User {user_id} rejected - email task queued")
                
            except Exception as task_error:
                logger.error(f"Failed to queue rejection email task: {str(task_error)}")
            
            # Return immediately (fast response)
            return Response({
                'message': 'User application rejected',
                'email_queued': True,
                'user': {
                    'email': user_data['email'],
                    'name': f"{user_data['first_name']} {user_data['last_name']}"
                }
            }, status=status.HTTP_200_OK)
            
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found or already processed'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error rejecting user {user_id}: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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


class UserCreateView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserDetailSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data)


class UserUpdateView(APIView):
    """Allow users to update their own profile information"""
    permission_classes = [IsAuthenticated]
    
    def put(self, request):
        user = request.user
        serializer = UserDetailSerializer(user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            
            # Send status update notification if online status changed
            try:
                from auth_app.models import Profile
                profile, created = Profile.objects.get_or_create(user=user)
                
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f'user_{user.id}',
                    {
                        'type': 'profile_update',
                        'message': {
                            'user_id': user.id,
                            'profile_updated': True,
                            'timestamp': timezone.now().isoformat()
                        }
                    }
                )
            except Exception as ws_error:
                logger.error(f"WebSocket profile update notification failed: {str(ws_error)}")
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [IsAdminOrSuperAdmin]

    def get_queryset(self):
        user_type = self.request.query_params.get('user_type')
        if user_type:
            return CustomUser.objects.filter(user_type=user_type)
        return CustomUser.objects.all()


class PendingAlumniListView(ListAPIView):
    serializer_class = UserDetailSerializer
    permission_classes = [IsAdminOrSuperAdmin]

    def get_queryset(self):
        cache_key = 'pending_alumni_list'
        cached_data = cache.get(cache_key)
        if cached_data:
            return CustomUser.objects.filter(id__in=cached_data)
        
        queryset = CustomUser.objects.filter(user_type=3, is_approved=False)
        user_ids = list(queryset.values_list('id', flat=True))
        cache.set(cache_key, user_ids, timeout=3600)
        return queryset


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
