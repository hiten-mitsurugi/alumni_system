# Import all view classes for backward compatibility
from .authentication import *
from .user_management import *
from .user_lists import *
from .alumni_directory import *
from .profile import *
from .social import *
from .utilities import *
from .admin import *
from .skills_work import *
from .additional import *

# Maintain backward compatibility by exposing all classes at module level
# This allows imports like: from auth_app.views import RegisterView
__all__ = [
    # Authentication views
    'RegisterView',
    'LoginView', 
    'LogoutView',
    'ConfirmTokenView',
    
    # User management views
    'ApproveUserView',
    'RejectUserView',
    'BlockUserView',
    'UnblockUserView',
    'UserCreateView',
    'UserUpdateView',
    
    # User list views
    'ApprovedAlumniListView',
    'PendingAlumniListView',
    'UserDetailView',
    'UserViewSet',
    
    # Alumni directory views
    'CheckAlumniDirectoryView',
    'AlumniDirectoryListCreateView',
    'AlumniDirectoryDetailView',
    'AlumniDirectoryImportView',
    
    # Profile views
    'ProfileView',
    'EnhancedProfileView',
    'ProfileSearchView',
    
    # Social views
    'FollowUserView',
    'UserConnectionsView',
    'NetworkSuggestionsView',
    'UserActivityView',
    
    # Utility views
    'UploadProfileImageView',
    'CheckStatusView',
    'ChangePasswordView',
    'UserStatsView',
    'BulkUserActionView',
    'ExportUsersView',
    'SystemHealthView',
    
    # Admin views
    'AdminDashboardView',
    'AdminUserAnalyticsView',
    'AdminConfigView',
    
    # Skills and Work views
    'SkillListCreateView',
    'WorkHistoryListCreateView',
    'WorkHistoryDetailView',
    'AchievementListCreateView',
    'AchievementDetailView',
    'EducationListCreateView',
    'EducationDetailView',
    
    # Additional views
    'SuggestedConnectionsView',
    'UserByNameView',
    'InvitationAcceptView',
    'InvitationRejectView',
    'TestStatusBroadcastView',
    'DebugUsersView',
    'ClearCacheView',
    'CheckEmailExistsView',
]