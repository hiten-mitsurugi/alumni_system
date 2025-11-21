from django.db.models.signals import post_save, post_delete, m2m_changed, pre_save
from django.dispatch import receiver
from django.core.cache import cache
from django.contrib.auth import get_user_model
from .models import SurveyCategory, SurveyQuestion, SurveyTemplate, SurveyTemplateCategory
from notifications_app.utils import create_notification

User = get_user_model()


# ========================================
# Cache Management
# ========================================

def clear_survey_caches():
    """Clear all survey-related caches when questions/categories/templates are modified"""
    try:
        cache.clear()
        print(f"🧹 Cleared all cache due to survey data changes")
    except Exception as e:
        print(f"⚠️ Error clearing cache: {e}")


# ========================================
# Survey Notification Handlers
# ========================================

def notify_alumni_of_new_survey(survey_template):
    """
    Notify all active alumni users when a new survey is published.
    Only notifies users with user_type=3 (Alumni).
    """
    alumni_users = User.objects.filter(user_type=3, is_active=True)
    
    notification_count = 0
    for user in alumni_users:
        try:
            create_notification(
                user=user,
                notification_type='survey',
                title='New Survey Available',
                message=f"A new survey '{survey_template.name}' has been published. Your response is appreciated!",
                link_route='/alumni/survey',
                link_params={'surveyId': survey_template.id},
                metadata={
                    'survey_name': survey_template.name,
                    'end_at': survey_template.end_at.isoformat() if survey_template.end_at else None
                }
            )
            notification_count += 1
        except Exception as e:
            print(f"⚠️ Failed to notify {user.email}: {e}")
    
    print(f"📢 Notified {notification_count} alumni about new survey: {survey_template.name}")


# ========================================
# Category Signal Receivers
# ========================================

@receiver(post_save, sender=SurveyCategory)
def handle_category_save(sender, instance, **kwargs):
    """Clear cache when a survey category is saved"""
    print(f"🗂️ SurveyCategory saved: {instance.name}")
    clear_survey_caches()


@receiver(post_delete, sender=SurveyCategory)
def handle_category_delete(sender, instance, **kwargs):
    """Clear cache when a survey category is deleted"""
    print(f"🗑️ SurveyCategory deleted: {instance.name}")
    clear_survey_caches()


# ========================================
# Question Signal Receivers
# ========================================

@receiver(post_save, sender=SurveyQuestion)
def handle_question_save(sender, instance, **kwargs):
    """Clear cache when a survey question is saved"""
    print(f"❓ SurveyQuestion saved: {instance.question_text[:50]}...")
    clear_survey_caches()


@receiver(post_delete, sender=SurveyQuestion)
def handle_question_delete(sender, instance, **kwargs):
    """Clear cache when a survey question is deleted"""
    print(f"🗑️ SurveyQuestion deleted: {instance.question_text[:50]}...")
    clear_survey_caches()


# ========================================
# Template Signal Receivers
# ========================================

# Store previous state for comparison
_survey_template_previous_state = {}

@receiver(pre_save, sender=SurveyTemplate)
def capture_template_previous_state(sender, instance, **kwargs):
    """
    Capture the previous published state before saving.
    This allows us to detect when a survey is being published for the first time.
    """
    if instance.pk:
        try:
            old_instance = SurveyTemplate.objects.get(pk=instance.pk)
            _survey_template_previous_state[instance.pk] = {
                'is_published': old_instance.is_published
            }
        except SurveyTemplate.DoesNotExist:
            _survey_template_previous_state[instance.pk] = {
                'is_published': False
            }
    else:
        _survey_template_previous_state[instance.pk] = {
            'is_published': False
        }


@receiver(post_save, sender=SurveyTemplate)
def handle_template_save(sender, instance, created, **kwargs):
    """
    Clear cache when a survey template is saved/published.
    Also notify alumni when a survey is published for the first time.
    """
    print(f"📋 SurveyTemplate saved: {instance.name} (published={instance.is_published})")
    clear_survey_caches()
    
    # Check if this is a new publication (transition from unpublished to published)
    previous_state = _survey_template_previous_state.get(instance.pk, {})
    was_published = previous_state.get('is_published', False)
    
    if instance.is_published and not was_published:
        # Survey was just published - notify all alumni
        print(f"🎉 Survey '{instance.name}' was just published, notifying alumni...")
        notify_alumni_of_new_survey(instance)
    
    # Clean up stored state
    if instance.pk in _survey_template_previous_state:
        del _survey_template_previous_state[instance.pk]


@receiver(post_delete, sender=SurveyTemplate)
def handle_template_delete(sender, instance, **kwargs):
    """
    When a SurveyTemplate (form) is deleted, check if any categories are now orphaned
    (not associated with any other template) and delete them.
    """
    print(f"🗑️ SurveyTemplate deleted: {instance.name}")
    
    # Find all categories that have no template associations
    orphaned_categories = SurveyCategory.objects.filter(
        surveytemplatecategory__isnull=True
    ).distinct()
    
    if orphaned_categories.exists():
        count = orphaned_categories.count()
        print(f"🧹 Found {count} orphaned categories, deleting them...")
        for category in orphaned_categories:
            print(f"  - Deleting orphaned category: {category.name}")
            category.delete()
        print(f"✅ Deleted {count} orphaned categories")
    else:
        print(f"✅ No orphaned categories found")
    
    clear_survey_caches()


# ========================================
# Template-Category Relationship Signal Receivers
# ========================================

@receiver(post_delete, sender=SurveyTemplateCategory)
def handle_template_category_delete(sender, instance, **kwargs):
    """
    When a SurveyTemplateCategory (relationship) is deleted,
    check if the category is now orphaned and delete it.
    """
    category = instance.category
    
    # Check if this category has any other template associations
    remaining_associations = SurveyTemplateCategory.objects.filter(
        category=category
    ).exists()
    
    if not remaining_associations:
        print(f"🧹 Category '{category.name}' is now orphaned (no template associations), deleting...")
        category.delete()
        print(f"✅ Deleted orphaned category: {category.name}")
    
    clear_survey_caches()


@receiver(m2m_changed, sender=SurveyTemplate.categories.through)
def handle_template_categories_change(sender, instance, action, **kwargs):
    """
    Clear cache when template-category relationships change.
    This ensures category changes appear immediately.
    """
    if action in ['post_add', 'post_remove', 'post_clear']:
        print(f"🔗 Template-Category relationship changed for: {instance.name}")
        clear_survey_caches()


