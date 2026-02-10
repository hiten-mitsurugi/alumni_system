# Generated migration to add description field to WorkHistory model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("auth_app", "0021_add_workhistory_description"),
    ]

    operations = [
        migrations.AddField(
            model_name="workhistory",
            name="description",
            field=models.TextField(blank=True, null=True),
        ),
    ]
