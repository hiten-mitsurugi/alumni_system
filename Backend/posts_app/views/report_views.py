"""
Report-related views for posts_app.

This module handles post reporting and admin report management.
"""

from django.core.cache import cache
from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ..models import Post, PostReport
from ..serializers import PostReportSerializer


class PostReportView(APIView):
    """Handle post reporting functionality"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, post_id):
        """Report a post"""
        try:
            post = Post.objects.get(id=post_id)
            
            # Check if user already reported this post
            existing_report = PostReport.objects.filter(
                post=post,
                reporter=request.user
            ).first()
            
            if existing_report:
                return Response(
                    {'error': 'You have already reported this post'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get report data
            reason = request.data.get('reason')
            details = request.data.get('details', '')
            
            if not reason:
                return Response(
                    {'error': 'Report reason is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create report
            report = PostReport.objects.create(
                post=post,
                reporter=request.user,
                reason=reason,
                description=details
            )
            
            # Serialize and return
            serializer = PostReportSerializer(report)
            
            return Response({
                'message': 'Post reported successfully. Thank you for helping keep our community safe.',
                'report': serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except Post.DoesNotExist:
            return Response(
                {'error': 'Post not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'An error occurred while processing your report: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdminReportListView(APIView):
    """Admin view to list all post reports"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get all post reports for admin review"""
        print(f"🔍 Reports API called by user: {request.user.username if request.user.is_authenticated else 'Anonymous'}")
        print(f"🔍 User type: {getattr(request.user, 'user_type', 'None')}")
        print(f"🔍 Is authenticated: {request.user.is_authenticated}")
        
        # Check if user is admin
        if not hasattr(request.user, 'user_type') or request.user.user_type not in [1, 2]:
            print(f"❌ Access denied for user {request.user.username}: not admin")
            return Response(
                {'error': 'Admin access required'}, 
                status=status.HTTP_403_FORBIDDEN
            )
            
        print(f"✅ Admin access granted for user {request.user.username}")
        
        try:
            # Get query parameters
            status_filter = request.query_params.get('status', 'pending')  # pending, resolved, all
            reason_filter = request.query_params.get('reason', '')
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 10))
            
            # Build queryset
            queryset = PostReport.objects.select_related('post', 'post__user', 'reporter', 'resolved_by')
            
            # Apply filters
            if status_filter == 'pending':
                queryset = queryset.filter(is_resolved=False)
            elif status_filter == 'resolved':
                queryset = queryset.filter(is_resolved=True)
            # 'all' shows everything
            
            if reason_filter:
                queryset = queryset.filter(reason=reason_filter)
            
            # Order by creation date (newest first)
            queryset = queryset.order_by('-created_at')
            
            # Pagination
            start = (page - 1) * page_size
            end = start + page_size
            reports = queryset[start:end]
            total_count = queryset.count()
            
            # Serialize data
            serializer = PostReportSerializer(reports, many=True)
            
            print(f"📊 Found {total_count} total reports, returning {len(reports)} for page {page}")
            print(f"📊 Serialized data length: {len(serializer.data)}")
            
            # Get statistics
            stats = {
                'total_reports': PostReport.objects.count(),
                'pending_reports': PostReport.objects.filter(is_resolved=False).count(),
                'resolved_today': PostReport.objects.filter(
                    is_resolved=True,
                    resolved_at__date=timezone.now().date()
                ).count(),
                'dismissed_today': PostReport.objects.filter(
                    is_resolved=True,
                    resolved_at__date=timezone.now().date(),
                    resolved_by__isnull=False
                ).count(),
            }
            
            return Response({
                'reports': serializer.data,
                'pagination': {
                    'page': page,
                    'page_size': page_size,
                    'total_count': total_count,
                    'total_pages': (total_count + page_size - 1) // page_size,
                    'has_more': end < total_count
                },
                'stats': stats
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'An error occurred while fetching reports: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdminReportActionView(APIView):
    """Admin view to take action on post reports"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, report_id):
        """Take action on a report: dismiss, warn user, or remove post"""
        # Check if user is admin
        if not hasattr(request.user, 'user_type') or request.user.user_type not in [1, 2]:
            return Response(
                {'error': 'Admin access required'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            report = PostReport.objects.select_related('post', 'post__user').get(id=report_id)
            
            if report.is_resolved:
                return Response(
                    {'error': 'This report has already been resolved'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            action = request.data.get('action')
            if action not in ['dismiss', 'warn', 'remove']:
                return Response(
                    {'error': 'Invalid action. Must be one of: dismiss, warn, remove'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Mark report as resolved
            report.is_resolved = True
            report.resolved_by = request.user
            report.resolved_at = timezone.now()
            report.save()
            
            response_message = ''
            
            if action == 'dismiss':
                response_message = 'Report dismissed successfully'
                
            elif action == 'warn':
                # Here you could implement user warning system
                # For now, just mark as resolved with warning
                response_message = 'User warned and report resolved'
                
            elif action == 'remove':
                # Remove the post
                post = report.post
                post.delete()
                response_message = 'Post removed and report resolved'
            
            # Update cache version
            cache.set('posts_cache_version', cache.get('posts_cache_version', 0) + 1)
            
            return Response({
                'message': response_message,
                'action': action,
                'report_id': report_id
            }, status=status.HTTP_200_OK)
            
        except PostReport.DoesNotExist:
            return Response(
                {'error': 'Report not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'An error occurred while processing the action: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
