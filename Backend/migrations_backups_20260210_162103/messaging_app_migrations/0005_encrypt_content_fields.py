# Generated migration for encrypting content fields

from django.db import migrations
from django_cryptography.fields import encrypt
import django.db.models


class Migration(migrations.Migration):

    dependencies = [
        ('messaging_app', '0004_messagerequest_content'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='content',
            field=encrypt(django.db.models.TextField()),
        ),
        migrations.AlterField(
            model_name='messagerequest',
            name='content',
            field=encrypt(django.db.models.TextField(blank=True, null=True)),
        ),
    ]
