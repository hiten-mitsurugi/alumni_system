from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import SurveyCategory, SurveyQuestion


def clear_survey_caches():
    """Clear all survey-related caches when questions/categories are modified"""
    cache_keys_to_clear = [
        'registration_survey_questions',  # Main registration cache
        'survey_analytics_data',          # Analytics cache
    ]
    
    for cache_key in cache_keys_to_clear:
        cache.delete(cache_key)
        print(f"🔔 Signal cleared cache key: {cache_key}")  # Debug log
    
    print(f"📡 Signal cleared {len(cache_keys_to_clear)} cache keys")  # Debug log


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
