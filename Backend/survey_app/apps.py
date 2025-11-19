from django.apps import AppConfig


class SurveyAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'survey_app'
    verbose_name = 'Dynamic Survey System'
    
    def ready(self):
        """Import signals when the app is ready"""
        import survey_app.signals
