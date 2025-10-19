# Generated migration to fix address columns
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth_app', '0002_profile_bio_profile_last_seen_profile_status'),
    ]

    operations = [
        # Rename 'address' column to 'present_address' using raw SQL
        migrations.RunSQL(
            "ALTER TABLE auth_app_customuser RENAME COLUMN address TO present_address;",
            reverse_sql="ALTER TABLE auth_app_customuser RENAME COLUMN present_address TO address;"
        ),
        # Add permanent_address column
        migrations.RunSQL(
            "ALTER TABLE auth_app_customuser ADD COLUMN permanent_address TEXT;",
            reverse_sql="ALTER TABLE auth_app_customuser DROP COLUMN permanent_address;"
        ),
    ]
