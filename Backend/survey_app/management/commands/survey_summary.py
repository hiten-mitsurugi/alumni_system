from django.core.management.base import BaseCommand
from survey_app.models import SurveyCategory, SurveyQuestion

class Command(BaseCommand):
    help = 'Show summary of current survey structure'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== SURVEY MANAGEMENT SYSTEM SUMMARY ===\n'))
        
        categories = SurveyCategory.objects.all().order_by('order', 'name')
        total_questions = SurveyQuestion.objects.count()
        active_questions = SurveyQuestion.objects.filter(is_active=True).count()
        conditional_questions = SurveyQuestion.objects.filter(depends_on_question__isnull=False).count()
        
        self.stdout.write(f'📊 Total Categories: {categories.count()}')
        self.stdout.write(f'📝 Total Questions: {total_questions}')
        self.stdout.write(f'✅ Active Questions: {active_questions}')
        self.stdout.write(f'🔗 Conditional Questions: {conditional_questions}\n')
        
        for category in categories:
            questions = category.questions.all()
            active_q = questions.filter(is_active=True).count()
            conditional_q = questions.filter(depends_on_question__isnull=False).count()
            
            self.stdout.write(f'📁 {category.name}')
            self.stdout.write(f'   Order: {category.order} | Active: {"✅" if category.is_active else "❌"}')
            self.stdout.write(f'   Questions: {questions.count()} total, {active_q} active, {conditional_q} conditional')
            
            if questions.exists():
                question_types = {}
                for q in questions:
                    q_type = q.question_type
                    question_types[q_type] = question_types.get(q_type, 0) + 1
                
                types_str = ', '.join([f'{k}({v})' for k, v in question_types.items()])
                self.stdout.write(f'   Types: {types_str}')
            
            self.stdout.write('')
        
        self.stdout.write(self.style.SUCCESS('✅ Survey system is ready for use!'))
        self.stdout.write('🌐 Access via Admin/SuperAdmin Dashboard -> Survey Management')