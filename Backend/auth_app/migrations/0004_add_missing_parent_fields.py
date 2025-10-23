# Generated migration to add missing parent fields
# NOTE: This migration is now a no-op because these fields already exist in the database
# and are properly defined in the model
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth_app', '0003_fix_address_columns'),
    ]

    operations = [
        # No operations needed - parent fields already exist in database
        # This migration is kept for migration history consistency
    ]
