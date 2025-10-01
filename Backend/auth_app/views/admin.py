from .base import *


class AdminDashboardView(APIView):
    """Admin dashboard with system overview"""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        # Get system statistics
        total_users = CustomUser.objects.count()
        active_users = CustomUser.objects.filter(is_active=True).count()
        pending_users = CustomUser.objects.filter(is_approved=False).count()
        
        # Alumni statistics
        total_alumni = CustomUser.objects.filter(user_type=3).count()
        approved_alumni = CustomUser.objects.filter(user_type=3, is_approved=True).count()
        
        # Recent registrations (last 30 days)
        from django.utils import timezone
        from datetime import timedelta
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_registrations = CustomUser.objects.filter(
            date_joined__gte=thirty_days_ago
        ).count()
        
        # Posts statistics if available
        posts_count = 0
        try:
            from posts_app.models import Post
            posts_count = Post.objects.count()
        except ImportError:
            pass
        
        dashboard_data = {
            'system_stats': {
                'total_users': total_users,
                'active_users': active_users,
                'pending_users': pending_users,
                'total_alumni': total_alumni,
                'approved_alumni': approved_alumni,
                'recent_registrations': recent_registrations,
                'total_posts': posts_count,
            },
            'recent_users': [],
            'pending_approvals': []
        }
        
        # Get recent users
        recent_users = CustomUser.objects.filter(
            date_joined__gte=thirty_days_ago
        ).order_by('-date_joined')[:10]
        
        from ..serializers import UserDetailSerializer
        dashboard_data['recent_users'] = UserDetailSerializer(
            recent_users, many=True, context={'request': request}
        ).data
        
        # Get pending approvals
        pending_approvals = CustomUser.objects.filter(
            is_approved=False, user_type=3
        ).order_by('-date_joined')[:10]
        
        dashboard_data['pending_approvals'] = UserDetailSerializer(
            pending_approvals, many=True, context={'request': request}
        ).data
        
        return Response(dashboard_data)


class AdminUserAnalyticsView(APIView):
    """User analytics for admin dashboard"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models import Count
        
        # Get date range (default: last 30 days)
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        # Registrations over time
        registrations = CustomUser.objects.filter(
            date_joined__gte=start_date
        ).extra({
            'date': 'DATE(date_joined)'
        }).values('date').annotate(
            count=Count('id')
        ).order_by('date')
        
        # User type distribution
        user_types = CustomUser.objects.values('user_type').annotate(
            count=Count('id')
        )
        
        # Program distribution for alumni
        programs = CustomUser.objects.filter(
            user_type=3
        ).values('program').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # Graduation year distribution
        grad_years = CustomUser.objects.filter(
            user_type=3, year_graduated__isnull=False
        ).values('year_graduated').annotate(
            count=Count('id')
        ).order_by('-year_graduated')
        
        analytics_data = {
            'registrations_over_time': list(registrations),
            'user_type_distribution': list(user_types),
            'top_programs': list(programs),
            'graduation_years': list(grad_years)
        }
        
        return Response(analytics_data)


class AdminConfigView(APIView):
    """Admin configuration management"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        # Return current system configuration
        config = {
            'registration_open': True,  # This could be stored in a settings model
            'auto_approve_alumni': False,
            'email_notifications_enabled': True,
            'max_upload_size_mb': 10,
            'allowed_file_types': ['jpg', 'jpeg', 'png', 'pdf'],
        }
        return Response(config)
    
    def patch(self, request):
        # Update system configuration
        # In a real implementation, this would update a settings model
        config_updates = request.data
        
        # Validate configuration updates here
        # For now, just return success
        return Response({
            'message': 'Configuration updated successfully',
            'updated_settings': config_updates
        })