"""
User Management Views - Approve/Reject/Block/Unblock users, User CRUD operations
"""
from .base_imports import *

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
