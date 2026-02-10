# Generated manually on 2026-02-10

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("auth_app", "0035_migrate_publication_authors_and_workhistory"),
    ]

    operations = [
        # Add is_current_job column if it doesn't exist
        migrations.RunSQL(
            sql="""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name = 'auth_app_workhistory' 
                        AND column_name = 'is_current_job'
                    ) THEN
                        ALTER TABLE auth_app_workhistory 
                        ADD COLUMN is_current_job boolean DEFAULT false NOT NULL;
                    END IF;
                END $$;
            """,
            reverse_sql="ALTER TABLE auth_app_workhistory DROP COLUMN IF EXISTS is_current_job;",
        ),
        # Create M2M table for skills if it doesn't exist
        migrations.RunSQL(
            sql="""
                CREATE TABLE IF NOT EXISTS auth_app_workhistory_skills (
                    id bigserial PRIMARY KEY,
                    workhistory_id bigint NOT NULL,
                    skill_id bigint NOT NULL,
                    CONSTRAINT auth_app_workhistory_skills_workhistory_id_fkey 
                        FOREIGN KEY (workhistory_id) REFERENCES auth_app_workhistory(id) 
                        ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
                    CONSTRAINT auth_app_workhistory_skills_skill_id_fkey 
                        FOREIGN KEY (skill_id) REFERENCES auth_app_skill(id) 
                        ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
                    CONSTRAINT auth_app_workhistory_skills_workhistory_id_skill_id_key 
                        UNIQUE (workhistory_id, skill_id)
                );
                
                CREATE INDEX IF NOT EXISTS auth_app_workhistory_skills_workhistory_id_idx 
                    ON auth_app_workhistory_skills(workhistory_id);
                CREATE INDEX IF NOT EXISTS auth_app_workhistory_skills_skill_id_idx 
                    ON auth_app_workhistory_skills(skill_id);
            """,
            reverse_sql="DROP TABLE IF EXISTS auth_app_workhistory_skills;",
        ),
    ]
