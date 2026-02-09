# Import all views to maintain compatibility with existing imports
try:
    from .authentication import (
        RegisterView, LoginView, LogoutView, ConfirmTokenView, 
        CheckEmailExistsView, ForgotPasswordView, ChangePasswordView
    )
    from .user_management import (
        ApproveUserView, RejectUserView, BlockUserView, UnblockUserView,
        UserCreateView, UserDetailView, UserUpdateView, UserViewSet,
        PendingAlumniListView, ApprovedAlumniListView
    )
    # New modular structure - connections, profile, search
    from .connections import (
        FollowUserView, UserConnectionsView, InvitationManageView,
        InvitationAcceptView, InvitationRejectView, TestConnectionStatusView
    )
    from .profile import (
        ProfileView, EnhancedProfileView, DebugEducationView
    )
    from .search import (
        ProfileSearchView, SuggestedConnectionsView, UserByNameView,
        UserMentionSearchView
    )
    # Keep old profile_social.py import for backwards compatibility (if needed)
    # from .profile_social import ...
    from .skills_work import (
        SkillListCreateView, UserSkillListCreateView, UserSkillDetailView, 
        WorkHistoryListCreateView, WorkHistoryDetailView,
        AchievementListCreateView, AchievementDetailView, EducationListCreateView,
        EducationDetailView, MembershipListCreateView, MembershipDetailView,
        RecognitionListCreateView, RecognitionDetailView,
        TrainingListCreateView, TrainingDetailView,
        PublicationListCreateView, PublicationDetailView,
        CertificateListCreateView, CertificateDetailView, CSEStatusView
    )
    from .alumni_directory import (
        AlumniDirectoryListCreateView, AlumniDirectoryDetailView, 
        AlumniDirectoryImportView, CheckAlumniDirectoryView
    )
    from .admin_utilities import (
        AdminAnalyticsView, DebugUsersView, ClearCacheView, 
        TestStatusBroadcastView
    )
    from .field_privacy import (
        ProfileFieldUpdateView
    )
    from .privacy_management import (
        PrivacySettingsView, BulkPrivacyUpdateView
    )
    from .cv_export import export_cv
    from .simple_profile import SimpleProfileView
    from .survey_profile import (
        AddressListCreateView, AddressDetailView,
        SkillsRelevanceView, CurriculumRelevanceView,
        PerceptionFurtherStudiesView, FeedbackRecommendationsView
    )
except ImportError as e:
    # Fallback to importing from the original views.py if the modular structure fails
    print(f"WARNING: Import error in views/__init__.py: {e}")
    import traceback
    traceback.print_exc()
    import sys
    import os
    parent_dir = os.path.dirname(os.path.dirname(__file__))
    sys.path.insert(0, parent_dir)
    
    try:
        from ..views import *
    except ImportError:
        # If all imports fail, define empty classes to prevent complete failure
        from rest_framework.views import APIView
        
        class RegisterView(APIView): pass
        class LoginView(APIView): pass
        class LogoutView(APIView): pass
        # Add other necessary empty classes as needed

# Export all views for backwards compatibility
__all__ = [
    # Authentication
    'RegisterView', 'LoginView', 'LogoutView', 'ConfirmTokenView', 
    'CheckEmailExistsView', 'ForgotPasswordView', 'ChangePasswordView',
    
    # User Management
    'ApproveUserView', 'RejectUserView', 'BlockUserView', 'UnblockUserView',
    'UserCreateView', 'UserDetailView', 'UserUpdateView', 'UserViewSet',
    'PendingAlumniListView', 'ApprovedAlumniListView',
    
    # Profile & Social
    'ProfileView', 'EnhancedProfileView', 'FollowUserView', 'UserConnectionsView',
    'InvitationManageView', 'InvitationAcceptView', 'InvitationRejectView',
    'ProfileSearchView', 'SuggestedConnectionsView', 'UserByNameView',
    'UserMentionSearchView', 'TestConnectionStatusView', 'DebugEducationView',
    
    # Skills & Work
    'SkillListCreateView', 'UserSkillListCreateView', 'UserSkillDetailView',
    'WorkHistoryListCreateView', 'WorkHistoryDetailView',
    'AchievementListCreateView', 'AchievementDetailView', 'EducationListCreateView',
    'EducationDetailView', 'MembershipListCreateView', 'MembershipDetailView',
    'RecognitionListCreateView', 'RecognitionDetailView',
    'TrainingListCreateView', 'TrainingDetailView',
    'PublicationListCreateView', 'PublicationDetailView',
    'CertificateListCreateView', 'CertificateDetailView', 'CSEStatusView',
    
    # Alumni Directory
    'AlumniDirectoryListCreateView', 'AlumniDirectoryDetailView', 
    'AlumniDirectoryImportView', 'CheckAlumniDirectoryView',
    
    # Admin & Utilities
    'AdminAnalyticsView', 'DebugUsersView', 'ClearCacheView', 
    'TestStatusBroadcastView',
    
    # Privacy Management
    'ProfileFieldUpdateView', 'PrivacySettingsView', 'BulkPrivacyUpdateView',
    
    # CV Export & Simple Profile
    'export_cv', 'SimpleProfileView',
    
    # Survey & Profile Data
    'AddressListCreateView', 'AddressDetailView',
    'SkillsRelevanceView', 'CurriculumRelevanceView',
    'PerceptionFurtherStudiesView', 'FeedbackRecommendationsView'
]
