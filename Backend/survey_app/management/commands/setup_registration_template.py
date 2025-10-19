from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from survey_app.models import SurveyCategory, SurveyTemplate, SurveyTemplateCategory

User = get_user_model()


class Command(BaseCommand):
    help = 'Create default registration survey template'

    def handle(self, *args, **options):
        # Get or create super admin user
        super_admin = User.objects.filter(user_type=1).first()
        if not super_admin:
            super_admin = User.objects.create_user(
                username='admin',
                email='admin@example.com',
                password='admin123',
                user_type=1
            )

        # Create default registration template
        template, created = SurveyTemplate.objects.get_or_create(
            name='Alumni Tracer Survey',
            defaults={
                'description': 'Complete alumni tracer survey for registration',
                'is_active': True,
                'is_default': True,
                'created_by': super_admin
            }
        )

        if created:
            self.stdout.write('Created default registration survey template')
        else:
            template.is_default = True
            template.save()
            self.stdout.write('Updated existing template to be default')

        # Add all categories to the template
        categories = SurveyCategory.objects.filter(is_active=True).order_by('order')
        
        # Clear existing template categories
        SurveyTemplateCategory.objects.filter(template=template).delete()
        
        # Add categories to template
        for category in categories:
            SurveyTemplateCategory.objects.create(
                template=template,
                category=category,
                order=category.order
            )
            
        self.stdout.write(f'Added {categories.count()} categories to template')
        self.stdout.write(self.style.SUCCESS('Default registration template setup complete'))
