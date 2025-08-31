from django.urls import path
from . import views

app_name = 'survey_app'

urlpatterns = [
    # =============================================================================
    # ADMIN ENDPOINTS - Survey Management (Super Admin & Admin Only)
    # =============================================================================
    
    # Category Management
    path('admin/categories/', views.SurveyCategoryListCreateView.as_view(), name='admin-category-list'),
    path('admin/categories/<int:pk>/', views.SurveyCategoryDetailView.as_view(), name='admin-category-detail'),
    
    # Question Management
    path('admin/questions/', views.SurveyQuestionListCreateView.as_view(), name='admin-question-list'),
    path('admin/questions/<int:pk>/', views.SurveyQuestionDetailView.as_view(), name='admin-question-detail'),
    
    # Analytics & Responses
    path('admin/analytics/', views.SurveyResponseAnalyticsView.as_view(), name='admin-analytics'),
    path('admin/responses/', views.SurveyResponsesView.as_view(), name='admin-responses'),
    
    # Utility endpoints
    path('admin/export/', views.survey_export_view, name='admin-export'),
    path('admin/clear-cache/', views.clear_survey_cache_view, name='admin-clear-cache'),
    
    # =============================================================================
    # ALUMNI ENDPOINTS - Survey Taking (Alumni & Authenticated Users)
    # =============================================================================
    
    # Survey Questions & Responses
    path('active-questions/', views.ActiveSurveyQuestionsView.as_view(), name='active-questions'),
    path('registration-questions/', views.RegistrationSurveyQuestionsView.as_view(), name='registration-questions'),
    path('responses/', views.SurveyResponseSubmitView.as_view(), name='submit-responses'),
    path('my-responses/', views.UserSurveyResponsesView.as_view(), name='user-responses'),
    path('progress/', views.SurveyProgressView.as_view(), name='user-progress'),
]
