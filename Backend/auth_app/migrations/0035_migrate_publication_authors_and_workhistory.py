from django.db import migrations


def forwards(apps, schema_editor):
    import re

    Publication = apps.get_model('auth_app', 'Publication')
    Author = apps.get_model('auth_app', 'Author')
    # Backfill Publication.authors -> Publication.authors_m2m
    for pub in Publication.objects.all():
        authors_str = getattr(pub, 'authors', None)
        if not authors_str:
            continue
        # split on comma, semicolon, or ' and '
        parts = re.split(r',|;|\band\b', authors_str)
        for p in parts:
            name = p.strip()
            if not name:
                continue
            author, _ = Author.objects.get_or_create(name=name)
            pub.authors_m2m.add(author)

    # NOTE: WorkHistory.is_current_job is applied in a separate schema migration.
    # Backfilling that field will be handled after the schema migration runs.


def reverse(apps, schema_editor):
    Publication = apps.get_model('auth_app', 'Publication')
    # Clear the normalized relationships (reverse of the forward migration)
    for pub in Publication.objects.all():
        if hasattr(pub, 'authors_m2m'):
            pub.authors_m2m.clear()
    # No WorkHistory cleanup here; handled in its own migration.


class Migration(migrations.Migration):

    dependencies = [
        ('auth_app', '0034_author_alter_publication_options_and_more'),
    ]

    operations = [
        migrations.RunPython(forwards, reverse),
    ]
