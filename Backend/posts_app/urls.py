from django.urls import path
from .views import (
    PostListCreateView, PostDetailView, CommentListCreateView,
    ReplyListCreateView, ReactionCreateView, PostApprovalView, PostCreateView
)

urlpatterns = [
    path('posts/', PostListCreateView.as_view(), name='posts'),
    path('posts/<int:post_id>/', PostDetailView.as_view(), name='post_detail'),
    path('posts/<int:post_id>/comments/', CommentListCreateView.as_view(), name='comments'),
    path('comments/<int:comment_id>/replies/', ReplyListCreateView.as_view(), name='replies'),
    path('react/<str:content_type>/<int:object_id>/', ReactionCreateView.as_view(), name='react'),
    path('posts/approve/', PostApprovalView.as_view(), name='post_approval_list'),
    path('posts/approve/<int:post_id>/', PostApprovalView.as_view(), name='post_approval'),
    path('posts/create/', PostCreateView.as_view(), name='post_create'),
]