# Generated migration to fix NOT NULL constraints
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("auth_app", "0029_workhistory_college_education_relevant_and_more"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                ALTER TABLE auth_app_workhistory 
                ALTER COLUMN job_type DROP NOT NULL,
                ALTER COLUMN employment_status DROP NOT NULL,
                ALTER COLUMN how_got_job DROP NOT NULL,
                ALTER COLUMN monthly_income DROP NOT NULL,
                ALTER COLUMN length_of_service DROP NOT NULL,
                ALTER COLUMN college_education_relevant DROP NOT NULL;
            """,
            reverse_sql="""
                ALTER TABLE auth_app_workhistory 
                ALTER COLUMN job_type SET NOT NULL,
                ALTER COLUMN employment_status SET NOT NULL,
                ALTER COLUMN how_got_job SET NOT NULL,
                ALTER COLUMN monthly_income SET NOT NULL,
                ALTER COLUMN length_of_service SET NOT NULL,
                ALTER COLUMN college_education_relevant SET NOT NULL;
            """
        ),
    ]
