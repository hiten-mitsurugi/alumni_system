from django.urls import path
from .views import (
    PostFeedView, PostCreateView, PostDetailView, PostReactionView, 
    CommentCreateView, SharePostView, PostApprovalView, SavePostView,
    PostPinView, PostUnpinView, PostFeatureView, PostUnfeatureView, PostEditView,
    PostReportView, AdminReportListView, AdminReportActionView
)

urlpatterns = [
    # Feed and basic post operations
    path('', PostFeedView.as_view(), name='post-feed'),
    path('create/', PostCreateView.as_view(), name='post-create'),
    path('<int:post_id>/', PostDetailView.as_view(), name='post-detail'),
    
    # Reactions (Facebook-style)
    path('<int:post_id>/react/', PostReactionView.as_view(), name='post-react'),
    
    # Comments
    path('<int:post_id>/comment/', CommentCreateView.as_view(), name='post-comment'),
    
    # Sharing/Reposting
    path('<int:post_id>/share/', SharePostView.as_view(), name='post-share'),
    
    # Save/Bookmark posts
    path('<int:post_id>/save/', SavePostView.as_view(), name='post-save'),
    
    # Admin post approval
    path('pending/', PostApprovalView.as_view(), name='post-approval-list'),
    path('<int:post_id>/approve/', PostApprovalView.as_view(), name='post-approve'),
    path('<int:post_id>/decline/', PostApprovalView.as_view(), name='post-decline'),
    
    # Admin post management
    path('<int:post_id>/pin/', PostPinView.as_view(), name='post-pin'),
    path('<int:post_id>/unpin/', PostUnpinView.as_view(), name='post-unpin'),
    path('<int:post_id>/feature/', PostFeatureView.as_view(), name='post-feature'),
    path('<int:post_id>/unfeature/', PostUnfeatureView.as_view(), name='post-unfeature'),
    path('<int:post_id>/edit/', PostEditView.as_view(), name='post-edit'),
    
    # Post reporting
    path('<int:post_id>/report/', PostReportView.as_view(), name='post-report'),
    
    # Admin report management
    path('reports/', AdminReportListView.as_view(), name='admin-report-list'),
    path('reports/<int:report_id>/action/', AdminReportActionView.as_view(), name='admin-report-action'),
]