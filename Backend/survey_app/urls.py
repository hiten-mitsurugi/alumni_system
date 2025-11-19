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
    path('admin/analytics/category/', views.CategoryAnalyticsView.as_view(), name='category-analytics'),
    path('admin/analytics/category/pdf/', views.category_analytics_pdf_export, name='category-analytics-pdf'),
    path('admin/analytics/form/pdf/', views.form_analytics_pdf_export, name='form-analytics-pdf'),
    path('admin/responses/', views.SurveyResponsesView.as_view(), name='admin-responses'),
    
    # Comprehensive Analytics Dashboard
    path('admin/analytics/overview/', views.AnalyticsOverviewView.as_view(), name='analytics-overview'),
    path('admin/analytics/employability/', views.EmployabilityAnalyticsView.as_view(), name='analytics-employability'),
    path('admin/analytics/skills/', views.SkillsAnalyticsView.as_view(), name='analytics-skills'),
    path('admin/analytics/curriculum/', views.CurriculumAnalyticsView.as_view(), name='analytics-curriculum'),
    path('admin/analytics/studies/', views.StudiesAnalyticsView.as_view(), name='analytics-studies'),
    path('admin/analytics/competitiveness/', views.CompetitivenessAnalyticsView.as_view(), name='analytics-competitiveness'),
    path('admin/analytics/program-comparison/', views.ProgramComparisonAnalyticsView.as_view(), name='analytics-program-comparison'),
    path('admin/analytics/demographics/', views.DemographicsAnalyticsView.as_view(), name='analytics-demographics'),
    path('admin/analytics/filter-options/', views.AnalyticsFilterOptionsView.as_view(), name='analytics-filter-options'),
    path('admin/analytics/export/', views.AnalyticsExportView.as_view(), name='analytics-export'),
    path('admin/analytics/export-full/', views.AnalyticsFullReportView.as_view(), name='analytics-export-full'),
    
    # Utility endpoints
    path('admin/export/', views.survey_export_view, name='admin-export'),
    path('admin/clear-cache/', views.clear_survey_cache_view, name='admin-clear-cache'),
    # Form (Template) management
    path('admin/forms/', views.SurveyFormListCreateView.as_view(), name='admin-form-list'),
    path('admin/forms/<int:pk>/', views.SurveyFormDetailView.as_view(), name='admin-form-detail'),
    path('admin/forms/<int:pk>/publish/', views.SurveyFormPublishView.as_view(), name='admin-form-publish'),
    
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
