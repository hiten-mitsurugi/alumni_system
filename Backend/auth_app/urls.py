from django.urls import path
from .views import (
    LoginView, RegisterView, UserCreateView, ApproveUserView,ApprovedAlumniListView, RejectUserView,
    ConfirmTokenView, UserDetailView, LogoutView, SkillListCreateView,
    WorkHistoryListCreateView, WorkHistoryDetailView, BlockUserView, UnblockUserView,
    ProfileView, CheckAlumniDirectoryView, PendingAlumniListView  # ✅ Make sure this is imported
)

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('create-user/', UserCreateView.as_view(), name='create_user'),
    path('pending-alumni/', PendingAlumniListView.as_view(), name='pending_alumni'),
    path('approve-user/<int:user_id>/', ApproveUserView.as_view(), name='approve_user'),
    path('reject-user/<int:user_id>/', RejectUserView.as_view(), name='reject_user'),
    path('confirm/<str:token>/', ConfirmTokenView.as_view(), name='confirm_token'),
    path('user/', UserDetailView.as_view(), name='user_detail'),  # ✅ Keep only this
    path('logout/', LogoutView.as_view(), name='logout'),
    path('approved-users/', ApprovedAlumniListView.as_view(), name='approved-users'),
    path('skills/', SkillListCreateView.as_view(), name='skills'),
    path('work-history/', WorkHistoryListCreateView.as_view(), name='work_history_list_create'),
    path('work-history/<int:pk>/', WorkHistoryDetailView.as_view(), name='work_history_detail'),
    path('block-user/<int:user_id>/', BlockUserView.as_view(), name='block_user'),
    path('unblock-user/<int:user_id>/', UnblockUserView.as_view(), name='unblock_user'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('check-alumni-directory/', CheckAlumniDirectoryView.as_view(), name='check_alumni_directory'),
    path('pending-alumni/', PendingAlumniListView.as_view(), name='pending_alumni'),
]
