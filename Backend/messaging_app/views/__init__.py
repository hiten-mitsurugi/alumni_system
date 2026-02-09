"""
Messaging app views package.
Re-exports all view classes to maintain backward compatibility with existing imports.

This allows existing code to continue using:
    from messaging_app.views import ConversationListView, SendMessageView, etc.

Instead of requiring:
    from messaging_app.views.conversations import ConversationListView
    from messaging_app.views.messages import SendMessageView
"""

# Cache utilities (helper functions, not views)
from .cache_utils import (
    invalidate_unread_counts_cache,
    invalidate_unread_counts_for_users,
)

# Conversation views
from .conversations import (
    ConversationListView,
    ConversationUsersView,
)

# Message views
from .messages import (
    SendMessageView,
    MessageListView,
)

# Group chat views
from .groups import (
    GroupChatCreateView,
    GroupChatManageView,
    GroupMembersView,
    GroupChatListView,
)

# Request views
from .requests import (
    MessageRequestView,
    GroupMemberRequestView,
    GroupMemberRequestManageView,
)

# Blocking views
from .blocking import (
    BlockUserView,
)

# Search views
from .search import (
    SearchView,
    SearchUsersView,
    MessageSearchView,
)

# Message action views
from .message_actions import (
    PinMessageView,
    BumpMessageView,
    ForwardMessageView,
)

# Reaction views
from .reactions import (
    MessageReactionView,
    MessageReactionsListView,
)

# Read status views
from .read_status import (
    MarkMessageAsReadView,
    UnreadCountsView,
)

# Upload views
from .upload import (
    UploadView,
)

# Define __all__ to specify public API
__all__ = [
    # Cache utilities
    'invalidate_unread_counts_cache',
    'invalidate_unread_counts_for_users',
    
    # Conversation views
    'ConversationListView',
    'ConversationUsersView',
    
    # Message views
    'SendMessageView',
    'MessageListView',
    
    # Group chat views
    'GroupChatCreateView',
    'GroupChatManageView',
    'GroupMembersView',
    'GroupChatListView',
    
    # Request views
    'MessageRequestView',
    'GroupMemberRequestView',
    'GroupMemberRequestManageView',
    
    # Blocking views
    'BlockUserView',
    
    # Search views
    'SearchView',
    'SearchUsersView',
    'MessageSearchView',
    
    # Message action views
    'PinMessageView',
    'BumpMessageView',
    'ForwardMessageView',
    
    # Reaction views
    'MessageReactionView',
    'MessageReactionsListView',
    
    # Read status views
    'MarkMessageAsReadView',
    'UnreadCountsView',
    
    # Upload views
    'UploadView',
]
