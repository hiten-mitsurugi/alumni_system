from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models.skills_work_models import WorkHistory
from .models.profile_social_models import Profile


def update_profile_from_workhistory(user):
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        return

    # Prefer explicit is_current_job, fallback to end_date is None
    current = (
        WorkHistory.objects.filter(user=user, is_current_job=True).order_by('-start_date').first()
        or WorkHistory.objects.filter(user=user, end_date__isnull=True).order_by('-start_date').first()
    )

    if current:
        profile.present_occupation = current.occupation
        profile.employing_agency = current.employing_agency
        profile.present_employment_status = current.employment_status or profile.present_employment_status
        profile.save()


@receiver(post_save, sender=WorkHistory)
def workhistory_saved(sender, instance, **kwargs):
    update_profile_from_workhistory(instance.user)


@receiver(post_delete, sender=WorkHistory)
def workhistory_deleted(sender, instance, **kwargs):
    update_profile_from_workhistory(instance.user)
