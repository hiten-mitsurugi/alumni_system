from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Notification
from .serializers import NotificationSerializer


# ========================================
# Notification Creation
# ========================================

def create_notification(user, notification_type, title, message, link_route=None, link_params=None, metadata=None, actor=None):
    """
    Create a notification and broadcast it via WebSocket.
    
    Args:
        user: User object to notify
        notification_type: Type (connection, survey, profile, post, system)
        title: Notification title
        message: Notification message
        link_route: Frontend route (e.g., '/alumni/home')
        link_params: Dict of route params (e.g., {'postId': 5})
        metadata: Additional data dict
        actor: User who triggered this notification
    
    Returns:
        Notification object
    """
    notification = Notification.objects.create(
        user=user,
        actor=actor,
        type=notification_type,
        title=title,
        message=message,
        link_route=link_route or '',
        link_params=link_params or {},
        metadata=metadata or {}
    )
    
    # Broadcast via WebSocket
    broadcast_notification(user.id, notification)
    
    return notification


# ========================================
# WebSocket Broadcasting
# ========================================

def broadcast_notification(user_id, notification):
    """
    Broadcast notification to user's WebSocket channel.
    
    Args:
        user_id: User ID to send notification to
        notification: Notification object to broadcast
    """
    channel_layer = get_channel_layer()
    
    # Check if channel layer is available (Redis)
    if not channel_layer:
        print(f"⚠️ Channel layer not available, skipping WebSocket broadcast for user {user_id}")
        return
    
    notification_data = NotificationSerializer(notification).data
    
    try:
        async_to_sync(channel_layer.group_send)(
            f'user_{user_id}',
            {
                'type': 'notification.message',
                'notification': notification_data
            }
        )
        print(f"📡 Broadcasted notification to group 'user_{user_id}': {notification.title}")
    except Exception as e:
        print(f"⚠️ Failed to broadcast notification to user {user_id}: {e}")


# ========================================
# Bulk Operations
# ========================================

def create_bulk_notifications(users, notification_type, title, message, link_route=None, link_params=None, metadata=None):
    """
    Create and broadcast notifications for multiple users efficiently.
    
    Args:
        users: QuerySet or list of User objects
        notification_type: Type (connection, survey, profile, post, system)
        title: Notification title
        message: Notification message
        link_route: Frontend route
        link_params: Dict of route params
        metadata: Additional data dict
    
    Returns:
        List of created Notification objects
    """
    notifications = []
    
    for user in users:
        try:
            notification = create_notification(
                user=user,
                notification_type=notification_type,
                title=title,
                message=message,
                link_route=link_route,
                link_params=link_params,
                metadata=metadata
            )
            notifications.append(notification)
        except Exception as e:
            print(f"⚠️ Failed to create notification for user {user.id}: {e}")
    
    return notifications

