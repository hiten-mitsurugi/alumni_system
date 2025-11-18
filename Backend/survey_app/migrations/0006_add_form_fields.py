from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey_app', '0005_set_existing_registration_categories'),
    ]

    operations = [
        # SurveyTemplate additive fields
        migrations.AddField(
            model_name='surveytemplate',
            name='is_published',
            field=models.BooleanField(default=False, help_text='Whether this form is published and accepting responses'),
        ),
        migrations.AddField(
            model_name='surveytemplate',
            name='accepting_responses',
            field=models.BooleanField(default=True, help_text='Whether responses are currently accepted'),
        ),
        migrations.AddField(
            model_name='surveytemplate',
            name='start_at',
            field=models.DateTimeField(blank=True, help_text='Optional start datetime for accepting responses', null=True),
        ),
        migrations.AddField(
            model_name='surveytemplate',
            name='end_at',
            field=models.DateTimeField(blank=True, help_text='Optional end datetime for accepting responses', null=True),
        ),
        migrations.AddField(
            model_name='surveytemplate',
            name='confirmation_message',
            field=models.TextField(blank=True, default='', help_text='Message shown to respondents after submission'),
        ),
        migrations.AddField(
            model_name='surveytemplate',
            name='form_settings',
            field=models.JSONField(blank=True, default=dict, help_text='Flexible JSON settings for the form', null=True),
        ),

        # SurveyQuestion branching JSON
        migrations.AddField(
            model_name='surveyquestion',
            name='branching',
            field=models.JSONField(blank=True, default=dict, help_text='JSON mapping for branching (option -> target_category_id or action)', null=True),
        ),

        # SurveyResponse optional form FK
        migrations.AddField(
            model_name='surveyresponse',
            name='form',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name='form_responses', to='survey_app.surveytemplate'),
        ),
    ]
