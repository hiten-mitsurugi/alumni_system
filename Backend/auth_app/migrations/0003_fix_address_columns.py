# Generated migration to fix address columns
# NOTE: This migration is now a no-op because address fields have been moved
# to the separate Address model in later migrations (0010_remove_legacy_address_fields.py)
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth_app', '0002_profile_bio_profile_last_seen_profile_status'),
    ]

    operations = [
        # No operations needed - address handling moved to Address model
        # This migration is kept for migration history consistency
    ]
