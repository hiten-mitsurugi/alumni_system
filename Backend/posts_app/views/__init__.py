"""
Posts app views package.

This module exports all views for backward compatibility.
All existing imports will continue to work exactly as before.
"""

# Base classes
from .base_views import (
    IsAdminOrSuperAdmin,
    PostPagination,
)

# Feed views
from .feed_views import (
    PostFeedView,
    PostCreateView,
    PostDetailView,
)

# Reaction views
from .reaction_views import (
    PostReactionView,
    CommentReactionView,
)

# Comment views
from .comment_views import (
    CommentCreateView,
    CommentDeleteView,
)

# Sharing views
from .sharing_views import (
    PostShareView,
    PostRepostView,
)

# Admin views
from .admin_views import (
    PostApprovalView,
    PostPinView,
    PostDeleteView,
)

# Report views
from .report_views import (
    PostReportView,
    AdminReportListView,
    AdminReportActionView,
)

# Utility views
from .utility_views import (
    SavePostView,
)

__all__ = [
    # Base classes
    'IsAdminOrSuperAdmin',
    'PostPagination',
    # Feed views
    'PostFeedView',
    'PostCreateView',
    'PostDetailView',
    # Reaction views
    'PostReactionView',
    'CommentReactionView',
    # Comment views
    'CommentCreateView',
    'CommentDeleteView',
    # Sharing views
    'PostShareView',
    'PostRepostView',
    # Admin views
    'PostApprovalView',
    'PostPinView',
    'PostDeleteView',
    # Report views
    'PostReportView',
    'AdminReportListView',
    'AdminReportActionView',
    # Utility views
    'SavePostView',
]
