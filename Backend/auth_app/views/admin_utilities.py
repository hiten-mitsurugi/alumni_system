"""
Admin Utilities Views - Debug, cache management, analytics, testing utilities
"""
from .base_imports import *

class AdminAnalyticsView(APIView):
    """Get analytics data for admin dashboard"""
    permission_classes = [IsAdminOrSuperAdmin]
    
    def get(self, request):
        try:
            from datetime import timedelta
            from posts_app.models import Post
            
            # Get basic user statistics
            total_users = CustomUser.objects.count()
            approved_alumni = CustomUser.objects.filter(user_type=3, is_approved=True).count()
            pending_alumni = CustomUser.objects.filter(user_type=3, is_approved=False).count()
            blocked_users = CustomUser.objects.filter(is_active=False).count()
            
            # Active users should match the same scope as total users for percentage calculation
            active_users = CustomUser.objects.filter(is_active=True).count()
            
            # Get user registration trends (last 7 days for "this week")
            seven_days_ago = timezone.now() - timedelta(days=7)
            recent_registrations = CustomUser.objects.filter(
                user_type=3, 
                is_approved=True,
                date_joined__gte=seven_days_ago
            ).count()
            
            # Get online users (active in last 15 minutes)
            fifteen_minutes_ago = timezone.now() - timedelta(minutes=15)
            online_users = CustomUser.objects.filter(
                last_login__gte=fifteen_minutes_ago
            ).count()
            
            # Get posts statistics
            total_posts = Post.objects.count()
            pending_posts = Post.objects.filter(status='pending').count()
            approved_posts = Post.objects.filter(status='approved').count()
            declined_posts = Post.objects.filter(status='declined').count()
            
            # Get weekly posts (last 7 days)
            weekly_posts = Post.objects.filter(
                created_at__gte=seven_days_ago
            ).count()
            
            # Get reported posts count (unresolved reports)
            try:
                from posts_app.models import PostReport
                reported_posts = PostReport.objects.filter(is_resolved=False).count()
            except:
                reported_posts = 0
            
            # Calculate approval rate
            total_reviewed = approved_posts + declined_posts
            approval_rate = round((approved_posts / total_reviewed * 100), 1) if total_reviewed > 0 else 0
            
            # Calculate user engagement (online/active ratio)
            user_engagement = round((online_users / active_users * 100), 1) if active_users > 0 else 0
            
            # Calculate pending actions
            pending_actions = pending_alumni + reported_posts
            
            # Get work history statistics
            total_work_histories = WorkHistory.objects.count()
            
            # Get skills statistics
            total_skills = Skill.objects.count()
            
            # Get employment status breakdown
            employment_stats = {}
            for status in ['employed_locally', 'employed_internationally', 'self_employed', 'unemployed', 'retired']:
                count = CustomUser.objects.filter(
                    user_type=3, 
                    is_approved=True, 
                    employment_status=status
                ).count()
                employment_stats[status] = count
            
            # Get gender breakdown
            gender_stats = {}
            for gender in ['male', 'female']:
                count = CustomUser.objects.filter(
                    user_type=3, 
                    is_approved=True, 
                    sex=gender
                ).count()
                gender_stats[gender] = count
            
            # Get year graduation distribution (last 10 years)
            current_year = timezone.now().year
            year_stats = {}
            for year in range(current_year - 10, current_year + 1):
                count = CustomUser.objects.filter(
                    user_type=3, 
                    is_approved=True, 
                    year_graduated=year
                ).count()
                if count > 0:
                    year_stats[str(year)] = count
            
            # Return data in the format frontend expects
            analytics_data = {
                'users': {
                    'total': total_users,  # Total all users (for activity rate calculation)
                    'active': active_users,  # Active users
                    'pending_approvals': pending_alumni,  # Pending alumni approvals
                    'recent_registrations': recent_registrations,  # New approved alumni this week
                    'online_now': online_users  # Currently online users
                },
                'posts': {
                    'total': total_posts,
                    'pending': pending_posts,
                    'approved': approved_posts,
                    'declined': declined_posts,
                    'reported': reported_posts,
                    'weekly_posts': weekly_posts,
                    'approval_rate': approval_rate
                },
                'summary': {
                    'user_engagement': user_engagement,
                    'pending_actions': pending_actions,
                    'total_users': total_users,
                    'approved_alumni': approved_alumni,  # Add this for reference
                    'total_content': total_posts
                },
                'content_statistics': {
                    'total_work_histories': total_work_histories,
                    'total_skills': total_skills
                },
                'demographics': {
                    'employment_status': employment_stats,
                    'gender_distribution': gender_stats,
                    'graduation_years': year_stats
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


class TestStatusBroadcastView(APIView):
    """Test endpoint to manually broadcast status updates"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            from auth_app.models import Profile
            
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
