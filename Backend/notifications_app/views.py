from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for listing and managing user notifications.
    Endpoints:
    - GET /api/notifications/ - List user's notifications (paginated)
    - GET /api/notifications/unread-count/ - Get unread count
    - PATCH /api/notifications/{id}/mark-as-read/ - Mark one as read
    - POST /api/notifications/mark-all-read/ - Mark all as read
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return notifications for current user only"""
        user = self.request.user
        queryset = Notification.objects.filter(user=user)
        
        # Filter by read status
        read_param = self.request.query_params.get('read', None)
        if read_param == 'false':
            queryset = queryset.filter(read_at__isnull=True)
        elif read_param == 'true':
            queryset = queryset.filter(read_at__isnull=False)
        
        # Filter by type
        type_param = self.request.query_params.get('type', None)
        if type_param:
            queryset = queryset.filter(type=type_param)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread notifications"""
        count = Notification.objects.filter(
            user=request.user,
            read_at__isnull=True
        ).count()
        return Response({'count': count})
    
    @action(detail=True, methods=['patch'])
    def mark_as_read(self, request, pk=None):
        """Mark a single notification as read"""
        notification = self.get_object()
        notification.mark_as_read()
        serializer = self.get_serializer(notification)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read"""
        from django.utils import timezone
        count = Notification.objects.filter(
            user=request.user,
            read_at__isnull=True
        ).update(read_at=timezone.now())
        return Response({'marked_read': count})

