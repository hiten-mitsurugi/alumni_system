from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    LoginView, RegisterView, UserCreateView, ApproveUserView, ApprovedAlumniListView, RejectUserView,
    ConfirmTokenView, UserDetailView, LogoutView, SkillListCreateView,
    WorkHistoryListCreateView, WorkHistoryDetailView, BlockUserView, UnblockUserView,
    ProfileView, CheckAlumniDirectoryView, PendingAlumniListView, UserViewSet, TestStatusBroadcastView,
    AlumniDirectoryListCreateView, AlumniDirectoryDetailView, AlumniDirectoryImportView,
    # LinkedIn-style views
    EnhancedProfileView, FollowUserView, UserConnectionsView, AchievementListCreateView,
    AchievementDetailView, EducationListCreateView, EducationDetailView, ProfileSearchView,
    SuggestedConnectionsView, UserByNameView
)

router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),  # Adds /api/auth/users/
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('create-user/', UserCreateView.as_view(), name='create_user'),
    path('pending-alumni/', PendingAlumniListView.as_view(), name='pending_alumni'),
    path('approve-user/<int:user_id>/', ApproveUserView.as_view(), name='approve_user'),
    path('reject-user/<int:user_id>/', RejectUserView.as_view(), name='reject_user'),
    path('confirm/<str:token>/', ConfirmTokenView.as_view(), name='confirm_token'),
    path('user/', UserDetailView.as_view(), name='user_detail'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('approved-users/', ApprovedAlumniListView.as_view(), name='approved-users'),
    path('skills/', SkillListCreateView.as_view(), name='skills'),
    path('work-history/', WorkHistoryListCreateView.as_view(), name='work_history_list_create'),
    path('work-history/<int:pk>/', WorkHistoryDetailView.as_view(), name='work_history_detail'),
    path('block-user/<int:user_id>/', BlockUserView.as_view(), name='block_user'),
    path('unblock-user/<int:user_id>/', UnblockUserView.as_view(), name='unblock_user'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('check-alumni-directory/', CheckAlumniDirectoryView.as_view(), name='check_alumni_directory'),
    path('test-status-broadcast/', TestStatusBroadcastView.as_view(), name='test_status_broadcast'),
    
    # Alumni Directory CRUD endpoints (SuperAdmin only)
    path('alumni-directory/import/', AlumniDirectoryImportView.as_view(), name='alumni_directory_import'),
    path('alumni-directory/', AlumniDirectoryListCreateView.as_view(), name='alumni_directory_list_create'),
    path('alumni-directory/<int:id>/', AlumniDirectoryDetailView.as_view(), name='alumni_directory_detail'),
    
    # LinkedIn-style Profile and Social Features  
    path('enhanced-profile/', EnhancedProfileView.as_view(), name='enhanced_profile'),
    path('enhanced-profile/<int:user_id>/', EnhancedProfileView.as_view(), name='enhanced_profile_user'),
    path('enhanced-profile/username/<str:username>/', EnhancedProfileView.as_view(), name='enhanced_profile_username'),
    path('follow/<int:user_id>/', FollowUserView.as_view(), name='follow_user'),
    path('connections/', UserConnectionsView.as_view(), name='user_connections'),
    path('connections/<int:user_id>/', UserConnectionsView.as_view(), name='user_connections_by_id'),
    
    # Achievements endpoints
    path('achievements/', AchievementListCreateView.as_view(), name='achievements_list_create'),
    path('achievements/<int:pk>/', AchievementDetailView.as_view(), name='achievement_detail'),
    path('achievements/user/<int:user_id>/', AchievementListCreateView.as_view(), name='user_achievements'),
    
    # Education endpoints
    path('education/', EducationListCreateView.as_view(), name='education_list_create'),
    path('education/<int:pk>/', EducationDetailView.as_view(), name='education_detail'),
    path('education/user/<int:user_id>/', EducationListCreateView.as_view(), name='user_education'),
    
    # Search and suggestions
    path('profile-search/', ProfileSearchView.as_view(), name='profile_search'),
    path('suggested-connections/', SuggestedConnectionsView.as_view(), name='suggested_connections'),
    
    # User resolution by name for URL routing
    path('alumni/by-name/<str:user_name>/', UserByNameView.as_view(), name='user_by_name'),
    
    # JWT token refresh endpoint for frontend
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]