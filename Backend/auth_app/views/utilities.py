from .base import *


class UploadProfileImageView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        user = request.user
        serializer = ProfileImageUploadSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CheckStatusView(APIView):
    """Check if user is online/active"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        status_info = get_user_status(user)
        return Response(status_info)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            old_password = serializer.validated_data['old_password']
            new_password = serializer.validated_data['new_password']
            
            if not user.check_password(old_password):
                return Response({'old_password': ['Wrong password.']}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(new_password)
            user.save()
            
            return Response({'message': 'Password changed successfully.'}, 
                          status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserStatsView(APIView):
    """Get user statistics"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        # Get basic stats
        stats = {
            'followers_count': 0,
            'following_count': 0,
            'posts_count': 0,
            'profile_views': 0
        }
        
        # Try to get Follow model stats if it exists
        try:
            from ..models import Follow
            stats['followers_count'] = Follow.objects.filter(following=user).count()
            stats['following_count'] = Follow.objects.filter(follower=user).count()
        except ImportError:
            pass
        
        # Try to get Post model stats if it exists
        try:
            from posts_app.models import Post
            stats['posts_count'] = Post.objects.filter(author=user).count()
        except ImportError:
            pass
        
        # Profile views from profile model if available
        if hasattr(user, 'profile') and hasattr(user.profile, 'view_count'):
            stats['profile_views'] = user.profile.view_count
        
        return Response(stats)


class BulkUserActionView(APIView):
    """Bulk operations for user management"""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        action = request.data.get('action')
        user_ids = request.data.get('user_ids', [])
        
        if not action or not user_ids:
            return Response({'error': 'Action and user_ids required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        users = CustomUser.objects.filter(id__in=user_ids)
        
        if action == 'approve':
            users.update(is_approved=True)
        elif action == 'block':
            users.update(is_active=False)
        elif action == 'unblock':
            users.update(is_active=True)
        elif action == 'delete':
            users.delete()
            return Response({'message': f'Deleted {len(user_ids)} users'})
        else:
            return Response({'error': 'Invalid action'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'message': f'Applied {action} to {users.count()} users'})


class ExportUsersView(APIView):
    """Export user data to CSV"""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="users_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Username', 'Email', 'First Name', 'Last Name', 
            'User Type', 'Is Approved', 'Is Active', 'Date Joined'
        ])
        
        users = CustomUser.objects.all().order_by('id')
        for user in users:
            writer.writerow([
                user.id, user.username, user.email, user.first_name, 
                user.last_name, user.get_user_type_display(), 
                user.is_approved, user.is_active, user.date_joined
            ])
        
        return response


class SystemHealthView(APIView):
    """System health check for admins"""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        health_data = {
            'database_status': 'healthy',
            'total_users': CustomUser.objects.count(),
            'active_users': CustomUser.objects.filter(is_active=True).count(),
            'approved_alumni': CustomUser.objects.filter(
                user_type=3, is_approved=True
            ).count(),
            'pending_approvals': CustomUser.objects.filter(
                user_type=3, is_approved=False
            ).count(),
        }
        
        # Check cache if available
        try:
            cache.set('health_check', True, timeout=1)
            if cache.get('health_check'):
                health_data['cache_status'] = 'healthy'
            else:
                health_data['cache_status'] = 'error'
        except:
            health_data['cache_status'] = 'unavailable'
        
        return Response(health_data)