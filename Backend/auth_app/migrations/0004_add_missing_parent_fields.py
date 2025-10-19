# Generated migration to add missing parent fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth_app', '0003_fix_address_columns'),
    ]

    operations = [
        # Add missing parent fields using raw SQL
        migrations.RunSQL(
            "ALTER TABLE auth_app_customuser ADD COLUMN mothers_name VARCHAR(150);",
            reverse_sql="ALTER TABLE auth_app_customuser DROP COLUMN mothers_name;"
        ),
        migrations.RunSQL(
            "ALTER TABLE auth_app_customuser ADD COLUMN mothers_occupation VARCHAR(100);",
            reverse_sql="ALTER TABLE auth_app_customuser DROP COLUMN mothers_occupation;"
        ),
        migrations.RunSQL(
            "ALTER TABLE auth_app_customuser ADD COLUMN fathers_name VARCHAR(150);",
            reverse_sql="ALTER TABLE auth_app_customuser DROP COLUMN fathers_name;"
        ),
        migrations.RunSQL(
            "ALTER TABLE auth_app_customuser ADD COLUMN fathers_occupation VARCHAR(100);",
            reverse_sql="ALTER TABLE auth_app_customuser DROP COLUMN fathers_occupation;"
        ),
    ]
