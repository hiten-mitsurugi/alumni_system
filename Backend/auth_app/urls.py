from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    LoginView, RegisterView, UserCreateView, ApproveUserView, ApprovedAlumniListView, RejectUserView,
    ConfirmTokenView, UserDetailView, LogoutView, SkillListCreateView, UserSkillListCreateView, UserSkillDetailView,
    WorkHistoryListCreateView, WorkHistoryDetailView, BlockUserView, UnblockUserView,
    ProfileView, CheckAlumniDirectoryView, PendingAlumniListView, UserViewSet, TestStatusBroadcastView,
    AlumniDirectoryListCreateView, AlumniDirectoryDetailView, AlumniDirectoryImportView, DebugUsersView, ClearCacheView,
    CheckEmailExistsView, AdminAnalyticsView, ForgotPasswordView, ChangePasswordView,
    # LinkedIn-style views
    FollowUserView, AchievementListCreateView,
    AchievementDetailView, EducationListCreateView, EducationDetailView, ProfileSearchView,
    SuggestedConnectionsView, UserByNameView,
    # Membership views
    MembershipListCreateView, MembershipDetailView,
    RecognitionListCreateView, RecognitionDetailView,
    TrainingListCreateView, TrainingDetailView,
    PublicationListCreateView, PublicationDetailView,
    CertificateListCreateView, CertificateDetailView, CSEStatusView,
    # Additional views for comprehensive model coverage (temporarily commented out)
    # AddressListCreateView, AddressDetailView, SkillsRelevanceView, CurriculumRelevanceView,
    # PerceptionStudiesView, FeedbackView
)

# Import CV export view
from .views.cv_export import export_cv

# Import the working EnhancedProfileView and UserConnectionsView from profile_social module
from .views.profile_social import (
    EnhancedProfileView, UserMentionSearchView, UserConnectionsView, 
    InvitationAcceptView, InvitationRejectView, TestConnectionStatusView
)

# Import field privacy views
from .views_field_privacy import ProfileFieldUpdateView, ProfileAboutDataView, UserAddressesView



router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),  # Adds /api/auth/users/
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('create-user/', UserCreateView.as_view(), name='create_user'),
    path('pending-alumni/', PendingAlumniListView.as_view(), name='pending_alumni'),
    path('approve-user/<int:user_id>/', ApproveUserView.as_view(), name='approve_user'),
    path('reject-user/<int:user_id>/', RejectUserView.as_view(), name='reject_user'),
    path('confirm/<str:token>/', ConfirmTokenView.as_view(), name='confirm_token'),
    path('user/', UserDetailView.as_view(), name='user_detail'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('approved-users/', ApprovedAlumniListView.as_view(), name='approved-users'),
    path('skills/', SkillListCreateView.as_view(), name='skills'),
    path('user-skills/', UserSkillListCreateView.as_view(), name='user_skills_list_create'),
    path('user-skills/<int:pk>/', UserSkillDetailView.as_view(), name='user_skill_detail'),
    path('work-history/', WorkHistoryListCreateView.as_view(), name='work_history_list_create'),
    path('work-history/<int:pk>/', WorkHistoryDetailView.as_view(), name='work_history_detail'),
    path('block-user/<int:user_id>/', BlockUserView.as_view(), name='block_user'),
    path('unblock-user/<int:user_id>/', UnblockUserView.as_view(), name='unblock_user'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('check-alumni-directory/', CheckAlumniDirectoryView.as_view(), name='check_alumni_directory'),
    path('test-status-broadcast/', TestStatusBroadcastView.as_view(), name='test_status_broadcast'),
    path('debug-users/', DebugUsersView.as_view(), name='debug_users'),
    path('admin/analytics/', AdminAnalyticsView.as_view(), name='admin_analytics'),
    path('clear-cache/', ClearCacheView.as_view(), name='clear_cache'),
    path('check-email/', CheckEmailExistsView.as_view(), name='check_email'),
    
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
    
    # Invitation management
    path('invitations/<int:invitation_id>/accept/', InvitationAcceptView.as_view(), name='accept_invitation'),
    path('invitations/<int:invitation_id>/reject/', InvitationRejectView.as_view(), name='reject_invitation'),
    
    # Test/Debug endpoints
    path('test-connection/<int:user_id>/', TestConnectionStatusView.as_view(), name='test_connection_status'),
    
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
    path('mention-search/', UserMentionSearchView.as_view(), name='user_mention_search'),
    
    # User resolution by name for URL routing
    path('alumni/by-name/<str:user_name>/', UserByNameView.as_view(), name='user_by_name'),
    
    # JWT token refresh endpoint for frontend
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Field Privacy and Profile Update endpoints
    path('profile/field-update/', ProfileFieldUpdateView.as_view(), name='profile_field_update'),
    path('profile/about-data/', ProfileAboutDataView.as_view(), name='profile_about_data'),
    path('profile/about-data/<int:user_id>/', ProfileAboutDataView.as_view(), name='profile_about_data_user'),
    path('profile/export-cv/', export_cv, name='export_cv'),  # CV PDF export
    
    # Address endpoints
    path('profile/<int:user_id>/addresses/', UserAddressesView.as_view(), name='user_addresses'),
    
    # Membership endpoints
    path('memberships/', MembershipListCreateView.as_view(), name='memberships_list_create'),
    path('memberships/<int:pk>/', MembershipDetailView.as_view(), name='membership_detail'),
    path('memberships/user/<int:user_id>/', MembershipListCreateView.as_view(), name='user_memberships'),
    
    # Recognition endpoints
    path('recognitions/', RecognitionListCreateView.as_view(), name='recognitions_list_create'),
    path('recognitions/<int:pk>/', RecognitionDetailView.as_view(), name='recognition_detail'),
    path('recognitions/user/<int:user_id>/', RecognitionListCreateView.as_view(), name='user_recognitions'),
    
    # Training endpoints
    path('trainings/', TrainingListCreateView.as_view(), name='trainings_list_create'),
    path('trainings/<int:pk>/', TrainingDetailView.as_view(), name='training_detail'),
    path('trainings/user/<int:user_id>/', TrainingListCreateView.as_view(), name='user_trainings'),
    
    # Publication endpoints
    path('publications/', PublicationListCreateView.as_view(), name='publications_list_create'),
    path('publications/<int:pk>/', PublicationDetailView.as_view(), name='publication_detail'),
    path('publications/user/<int:user_id>/', PublicationListCreateView.as_view(), name='user_publications'),
    
    # Certificate endpoints
    path('certificates/', CertificateListCreateView.as_view(), name='certificates_list_create'),
    path('certificates/<int:pk>/', CertificateDetailView.as_view(), name='certificate_detail'),
    path('certificates/user/<int:user_id>/', CertificateListCreateView.as_view(), name='user_certificates'),
    
    # CSE Status endpoint
    path('cse-status/', CSEStatusView.as_view(), name='cse_status'),

    
    # Survey and questionnaire endpoints (temporarily commented out)
    # path('skills-relevance/', SkillsRelevanceView.as_view(), name='skills_relevance'),
    # path('curriculum-relevance/', CurriculumRelevanceView.as_view(), name='curriculum_relevance'),
    # path('perception-studies/', PerceptionStudiesView.as_view(), name='perception_studies'),
    # path('feedback/', FeedbackView.as_view(), name='feedback'),
]