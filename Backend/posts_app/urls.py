from django.urls import path
from .views import (
    PostFeedView, PostCreateView, PostDetailView, PostReactionView, 
    CommentCreateView, SharePostView, PostApprovalView, SavePostView,
    PostReportView, AdminReportListView, AdminReportActionView
)

urlpatterns = [
    # Feed and basic post operations
    path('posts/', PostFeedView.as_view(), name='post-feed'),
    path('posts/create/', PostCreateView.as_view(), name='post-create'),
    path('posts/<int:post_id>/', PostDetailView.as_view(), name='post-detail'),
    
    # Reactions (Facebook-style)
    path('posts/<int:post_id>/react/', PostReactionView.as_view(), name='post-react'),
    path('posts/<int:post_id>/reactions/', PostReactionView.as_view(), name='post-reactions'),
    
    # Comments
    path('posts/<int:post_id>/comment/', CommentCreateView.as_view(), name='post-comment'),
    path('posts/<int:post_id>/comments/', CommentCreateView.as_view(), name='post-comments'),
    
    # Sharing/Reposting
    path('posts/<int:post_id>/share/', SharePostView.as_view(), name='post-share'),
    
    # Save/Bookmark posts
    path('posts/<int:post_id>/save/', SavePostView.as_view(), name='post-save'),
    
    # Admin post approval
    path('posts/pending/', PostApprovalView.as_view(), name='post-approval-list'),
    path('posts/<int:post_id>/approve/', PostApprovalView.as_view(), name='post-approve'),
    
    # Post reporting
    path('posts/<int:post_id>/report/', PostReportView.as_view(), name='post-report'),
    
    # Admin report management
    path('posts/reports/', AdminReportListView.as_view(), name='admin-report-list'),
    path('posts/reports/<int:report_id>/action/', AdminReportActionView.as_view(), name='admin-report-action'),
]