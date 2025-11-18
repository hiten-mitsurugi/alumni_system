from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('survey_app', '0007_surveycategory_page_break_and_more'),
    ]

    operations = [
        # Remove old fields that were replaced by new ones
        migrations.RemoveField(
            model_name='surveytemplate',
            name='response_start_date',
        ),
        migrations.RemoveField(
            model_name='surveytemplate',
            name='response_end_date',
        ),
        migrations.RemoveField(
            model_name='surveytemplate',
            name='allow_response_editing',
        ),
        migrations.RemoveField(
            model_name='surveytemplate',
            name='collect_email',
        ),
        migrations.RemoveField(
            model_name='surveytemplate',
            name='limit_one_response',
        ),
    ]
