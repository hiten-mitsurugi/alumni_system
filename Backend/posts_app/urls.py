from django.urls import path
from .views import (
    PostFeedView, PostCreateView, PostDetailView, PostReactionView, 
    CommentCreateView, CommentDeleteView, PostShareView, PostRepostView,
    PostApprovalView, SavePostView, PostReportView, AdminReportListView, 
    AdminReportActionView, PostPinView, PostDeleteView
)

urlpatterns = [
    # Feed and basic post operations
    path('', PostFeedView.as_view(), name='post-feed'),
    path('create/', PostCreateView.as_view(), name='post-create'),
    path('<int:post_id>/', PostDetailView.as_view(), name='post-detail'),
    
    # Reactions (Facebook-style)
    path('<int:post_id>/react/', PostReactionView.as_view(), name='post-react'),
    path('<int:post_id>/reactions/', PostReactionView.as_view(), name='post-reactions'),
    
    # Comments
    path('<int:post_id>/comment/', CommentCreateView.as_view(), name='post-comment'),
    path('<int:post_id>/comments/', CommentCreateView.as_view(), name='post-comments'),
    path('comments/<int:comment_id>/delete/', CommentDeleteView.as_view(), name='comment-delete'),
    
    # Share and Repost
    path('<int:post_id>/share/', PostShareView.as_view(), name='post-share'),
    path('<int:post_id>/repost/', PostRepostView.as_view(), name='post-repost'),
    
    # Save/Bookmark posts
    path('<int:post_id>/save/', SavePostView.as_view(), name='post-save'),
    
    # Admin post approval
    path('pending/', PostApprovalView.as_view(), name='post-approval-list'),
    path('<int:post_id>/approve/', PostApprovalView.as_view(), name='post-approve'),
    
    # Post reporting
    path('<int:post_id>/report/', PostReportView.as_view(), name='post-report'),
    
    # Admin report management
    path('reports/', AdminReportListView.as_view(), name='admin-report-list'),
    path('reports/<int:report_id>/action/', AdminReportActionView.as_view(), name='admin-report-action'),
    
    # Post management (pin/delete)
    path('<int:post_id>/pin/', PostPinView.as_view(), name='post-pin'),
    path('<int:post_id>/delete/', PostDeleteView.as_view(), name='post-delete'),
]