# Generated manually for adding content field to MessageRequest

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messaging_app', '0003_attachment_file_type_delete_userprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='messagerequest',
            name='content',
            field=models.TextField(blank=True, null=True),
        ),
    ]
