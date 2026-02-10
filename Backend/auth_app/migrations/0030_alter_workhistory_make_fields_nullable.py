# Generated migration to fix NOT NULL constraints
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("auth_app", "0029_workhistory_college_education_relevant_and_more"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                DO $$
                BEGIN
                    -- Drop NOT NULL constraints only if columns exist
                    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'auth_app_workhistory' AND column_name = 'job_type') THEN
                        ALTER TABLE auth_app_workhistory ALTER COLUMN job_type DROP NOT NULL;
                    END IF;
                    
                    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'auth_app_workhistory' AND column_name = 'employment_status') THEN
                        ALTER TABLE auth_app_workhistory ALTER COLUMN employment_status DROP NOT NULL;
                    END IF;
                    
                    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'auth_app_workhistory' AND column_name = 'how_got_job') THEN
                        ALTER TABLE auth_app_workhistory ALTER COLUMN how_got_job DROP NOT NULL;
                    END IF;
                    
                    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'auth_app_workhistory' AND column_name = 'monthly_income') THEN
                        ALTER TABLE auth_app_workhistory ALTER COLUMN monthly_income DROP NOT NULL;
                    END IF;
                    
                    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'auth_app_workhistory' AND column_name = 'length_of_service') THEN
                        ALTER TABLE auth_app_workhistory ALTER COLUMN length_of_service DROP NOT NULL;
                    END IF;
                    
                    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'auth_app_workhistory' AND column_name = 'college_education_relevant') THEN
                        ALTER TABLE auth_app_workhistory ALTER COLUMN college_education_relevant DROP NOT NULL;
                    END IF;
                END $$;
            """,
            reverse_sql="""
                DO $$
                BEGIN
                    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'auth_app_workhistory' AND column_name = 'job_type') THEN
                        ALTER TABLE auth_app_workhistory ALTER COLUMN job_type SET NOT NULL;
                    END IF;
                    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'auth_app_workhistory' AND column_name = 'employment_status') THEN
                        ALTER TABLE auth_app_workhistory ALTER COLUMN employment_status SET NOT NULL;
                    END IF;
                    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'auth_app_workhistory' AND column_name = 'how_got_job') THEN
                        ALTER TABLE auth_app_workhistory ALTER COLUMN how_got_job SET NOT NULL;
                    END IF;
                    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'auth_app_workhistory' AND column_name = 'monthly_income') THEN
                        ALTER TABLE auth_app_workhistory ALTER COLUMN monthly_income SET NOT NULL;
                    END IF;
                    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'auth_app_workhistory' AND column_name = 'length_of_service') THEN
                        ALTER TABLE auth_app_workhistory ALTER COLUMN length_of_service SET NOT NULL;
                    END IF;
                    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'auth_app_workhistory' AND column_name = 'college_education_relevant') THEN
                        ALTER TABLE auth_app_workhistory ALTER COLUMN college_education_relevant SET NOT NULL;
                    END IF;
                END $$;
            """
        ),
    ]
