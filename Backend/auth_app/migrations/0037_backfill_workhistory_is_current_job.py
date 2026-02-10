# Data migration to backfill WorkHistory.is_current_job from end_date

from django.db import migrations


def backfill_is_current_job(apps, schema_editor):
    WorkHistory = apps.get_model('auth_app', 'WorkHistory')
    
    for wh in WorkHistory.objects.all():
        # Set is_current_job = True if end_date is None
        is_current = (wh.end_date is None)
        if wh.is_current_job != is_current:
            wh.is_current_job = is_current
            wh.save(update_fields=['is_current_job'])


def reverse_backfill(apps, schema_editor):
    WorkHistory = apps.get_model('auth_app', 'WorkHistory')
    
    # Reset all to False on reverse
    WorkHistory.objects.all().update(is_current_job=False)


class Migration(migrations.Migration):
    dependencies = [
        ("auth_app", "0036_workhistory_is_current_job_workhistory_skills"),
    ]

    operations = [
        migrations.RunPython(backfill_is_current_job, reverse_backfill),
    ]
