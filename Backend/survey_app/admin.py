from django.contrib import admin
from django.utils.html import format_html
from .models import SurveyCategory, SurveyQuestion, SurveyResponse, SurveyTemplate


@admin.register(SurveyCategory)
class SurveyCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'is_active', 'active_questions_count', 'created_by', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['order', 'name']
    readonly_fields = ['created_by', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'order', 'is_active')
        }),
        ('Audit Information', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
        # No cache clearing needed - registration endpoint doesn't use cache
    
    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        # No cache clearing needed - registration endpoint doesn't use cache


@admin.register(SurveyQuestion)
class SurveyQuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text_short', 'category', 'question_type', 'is_required', 'is_active', 'order', 'response_count']
    list_filter = ['question_type', 'is_required', 'is_active', 'category', 'created_at']
    search_fields = ['question_text', 'category__name']
    ordering = ['category__order', 'order', 'question_text']
    readonly_fields = ['created_by', 'created_at', 'updated_at', 'response_count']
    
    fieldsets = (
        ('Question Details', {
            'fields': ('category', 'question_text', 'question_type', 'placeholder_text', 'help_text')
        }),
        ('Options & Validation', {
            'fields': ('options', 'is_required', 'min_value', 'max_value', 'max_length')
        }),
        ('Display Settings', {
            'fields': ('order', 'is_active')
        }),
        ('Audit Information', {
            'fields': ('created_by', 'created_at', 'updated_at', 'response_count'),
            'classes': ('collapse',)
        })
    )
    
    def question_text_short(self, obj):
        return obj.question_text[:50] + '...' if len(obj.question_text) > 50 else obj.question_text
    question_text_short.short_description = 'Question Text'
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
        # No cache clearing needed - registration endpoint doesn't use cache
    
    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        # No cache clearing needed - registration endpoint doesn't use cache


@admin.register(SurveyResponse)
class SurveyResponseAdmin(admin.ModelAdmin):
    list_display = ['user_email', 'question_short', 'response_preview', 'submitted_at']
    list_filter = ['question__category', 'question__question_type', 'submitted_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'question__question_text']
    readonly_fields = ['user', 'question', 'response_data', 'submitted_at', 'updated_at', 'ip_address']
    ordering = ['-submitted_at']
    
    fieldsets = (
        ('Response Information', {
            'fields': ('user', 'question', 'response_data')
        }),
        ('Metadata', {
            'fields': ('submitted_at', 'updated_at', 'ip_address'),
            'classes': ('collapse',)
        })
    )
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User'
    user_email.admin_order_field = 'user__email'
    
    def question_short(self, obj):
        return obj.question.question_text[:40] + '...' if len(obj.question.question_text) > 40 else obj.question.question_text
    question_short.short_description = 'Question'
    
    def response_preview(self, obj):
        display_value = obj.get_display_value()
        if len(str(display_value)) > 50:
            return str(display_value)[:50] + '...'
        return display_value
    response_preview.short_description = 'Response'
    
    def has_add_permission(self, request):
        # Responses should be created through the API, not admin
        return False
    
    def has_change_permission(self, request, obj=None):
        # Allow viewing but not editing
        return False


@admin.register(SurveyTemplate)
class SurveyTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'is_default', 'categories_count', 'created_by', 'created_at']
    list_filter = ['is_active', 'is_default', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_by', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Template Information', {
            'fields': ('name', 'description')
        }),
        ('Settings', {
            'fields': ('is_active', 'is_default')
        }),
        ('Audit Information', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def categories_count(self, obj):
        return obj.categories.count()
    categories_count.short_description = 'Categories'
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


# Customize admin site header
admin.site.site_header = 'Alumni System - Survey Management'
admin.site.site_title = 'Survey Admin'
admin.site.index_title = 'Dynamic Survey Administration'
