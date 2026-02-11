"""
Messaging app WebSocket consumers package.
Re-exports all consumer classes and helpers for backward compatibility with routing.py.
"""

# Base classes and utilities
from .utils import (
    ACTIVE_CONNECTIONS,
    parse_mentions,
    create_mentions,
    send_mention_notifications,
)
from .base import MessagingBaseMixin

# Handler mixins
from .private_handlers import PrivateMessageHandlersMixin
from .private_helpers import PrivateMessageHelpersMixin as PrivateHelpersMixin
from .group_handlers import GroupMessageHandlersMixin

# Main consumer classes
from .private_chat import PrivateChatConsumer
from .group_chat import GroupChatConsumer

__all__ = [
    # Consumer classes (used in routing.py)
    'PrivateChatConsumer',
    'GroupChatConsumer',
    
    # Base and mixins (for potential extensions)
    'MessagingBaseMixin',
    'PrivateMessageHandlersMixin',
    'PrivateHelpersMixin',
    'GroupMessageHandlersMixin',
    
    # Utilities (for testing and debugging)
    'ACTIVE_CONNECTIONS',
    'parse_mentions',
    'create_mentions',
    'send_mention_notifications',
]
