from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.core.cache import cache
from .models import SurveyCategory, SurveyQuestion, SurveyTemplate, SurveyTemplateCategory


def clear_survey_caches():
    """Clear all survey-related caches when questions/categories/templates are modified"""
    # Just clear the entire cache to ensure no stale data
    # This is simpler and more reliable than pattern matching
    try:
        cache.clear()
        print(f"🧹 Cleared all cache due to survey data changes")
    except Exception as e:
        print(f"⚠️ Error clearing cache: {e}")


@receiver(post_save, sender=SurveyCategory)
def clear_cache_on_category_save(sender, instance, **kwargs):
    """Clear cache when a survey category is saved"""
    print(f"🗂️ SurveyCategory saved: {instance.name}")
    clear_survey_caches()


@receiver(post_delete, sender=SurveyCategory)
def clear_cache_on_category_delete(sender, instance, **kwargs):
    """Clear cache when a survey category is deleted"""
    print(f"🗑️ SurveyCategory deleted: {instance.name}")
    clear_survey_caches()


@receiver(post_save, sender=SurveyQuestion)
def clear_cache_on_question_save(sender, instance, **kwargs):
    """Clear cache when a survey question is saved"""
    print(f"❓ SurveyQuestion saved: {instance.question_text[:50]}...")
    clear_survey_caches()


@receiver(post_delete, sender=SurveyQuestion)
def clear_cache_on_question_delete(sender, instance, **kwargs):
    """Clear cache when a survey question is deleted"""
    print(f"🗑️ SurveyQuestion deleted: {instance.question_text[:50]}...")
    clear_survey_caches()


@receiver(post_delete, sender=SurveyTemplate)
def delete_orphaned_categories_on_template_delete(sender, instance, **kwargs):
    """
    When a SurveyTemplate (form) is deleted, check if any categories are now orphaned
    (not associated with any other template) and delete them.
    """
    print(f"🗑️ SurveyTemplate deleted: {instance.name}")
    
    # Get all categories that were associated with this template
    # Note: This runs AFTER the template is deleted, so we can't get categories directly
    # Instead, we'll find all categories that have no template associations
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


@receiver(post_delete, sender=SurveyTemplateCategory)
def check_orphaned_category_on_relation_delete(sender, instance, **kwargs):
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


@receiver(post_save, sender=SurveyTemplate)
def clear_cache_on_template_save(sender, instance, **kwargs):
    """
    Clear cache when a survey template is saved/published.
    This ensures published forms appear immediately for users.
    """
    print(f"📋 SurveyTemplate saved: {instance.name} (published={instance.is_published})")
    clear_survey_caches()


@receiver(m2m_changed, sender=SurveyTemplate.categories.through)
def clear_cache_on_template_categories_changed(sender, instance, action, **kwargs):
    """
    Clear cache when template-category relationships change.
    This ensures category changes appear immediately.
    """
    if action in ['post_add', 'post_remove', 'post_clear']:
        print(f"🔗 Template-Category relationship changed for: {instance.name}")
        clear_survey_caches()
