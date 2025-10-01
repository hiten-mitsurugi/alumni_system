from .base import *
from .connection_mixin import ConnectionMixin
from .status_mixin import StatusMixin
from .notification_mixin import NotificationMixin
from .group_mixin import GroupMixin
from .user_mixin import UserMixin
from .message_mixin import MessageMixin


class NotificationConsumer(
    ConnectionMixin,
    StatusMixin,
    NotificationMixin,
    GroupMixin,
    UserMixin,
    MessageMixin,
    AsyncWebsocketConsumer
):
    """
    WebSocket consumer for handling notifications and real-time updates.
    
    Combines all mixin functionality:
    - Connection management (connect, disconnect, heartbeat)
    - Status updates (online/offline broadcasts)
    - General notifications and broadcasts
    - Group-related events and notifications
    - User management events (blocking/unblocking)
    - Message-related notifications (read receipts)
    
    This consumer handles all non-chat WebSocket events for the auth_app.
    For actual messaging (chat, group chat), use messaging_app consumers.
    """
    pass  # All functionality inherited from mixins