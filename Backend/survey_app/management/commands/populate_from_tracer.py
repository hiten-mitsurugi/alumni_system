import re
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from survey_app.models import SurveyCategory, SurveyQuestion

User = get_user_model()

class Command(BaseCommand):
    help = 'Intelligently populate survey categories and questions from tracer.txt (Alumni Tracer Survey) with proper conditional logic and question types'

    def add_arguments(self, parser):
        parser.add_argument(
            '--admin-email',
            type=str,
            default='admin@example.com',
            help='Email of the admin user who will be set as creator'
        )
        parser.add_argument(
            '--tracer-file',
            type=str,
            default='tracer.txt',
            help='Path to the tracer.txt file'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without actually creating it'
        )

    def handle(self, *args, **options):
        admin_email = options['admin_email']
        tracer_file = options['tracer_file']
        dry_run = options['dry_run']

        # Get or create admin user
        admin_user = User.objects.filter(user_type__in=[1, 2]).first()
        if not admin_user:
            if dry_run:
                self.stdout.write(self.style.WARNING('[DRY RUN] No admin user found. Would create default admin...'))
                admin_user = None
            else:
                self.stdout.write(self.style.WARNING('No admin user found. Creating default admin...'))
                admin_user = User.objects.create_user(
                    username='admin',
                    email=admin_email,
                    password='admin123',
                    user_type=1,
                    first_name='System',
                    last_name='Administrator',
                    is_approved=True
                )
                self.stdout.write(self.style.SUCCESS(f'Created admin user: {admin_email}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Using existing admin: {admin_user.email}'))

        # Find tracer.txt file
        if not os.path.exists(tracer_file):
            # Try to find it in the root directory
            root_tracer = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '..', '..', '..', 'tracer.txt')
            if os.path.exists(root_tracer):
                tracer_file = root_tracer
            else:
                self.stdout.write(self.style.ERROR(f'tracer.txt not found at {tracer_file} or {root_tracer}'))
                return

        # Read and parse tracer.txt
        try:
            with open(tracer_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error reading tracer.txt: {e}'))
            return

        self.stdout.write(self.style.SUCCESS(f'Successfully read tracer.txt from: {tracer_file}'))
        
        # Parse the content into structured data
        parsed_data = self.parse_tracer_content(content)
        
        if dry_run:
            self.show_dry_run_preview(parsed_data)
            return
        
        # Create categories and questions in the database
        self.create_survey_structure(parsed_data, admin_user)

    def parse_tracer_content(self, content):
        """Parse tracer.txt content into structured survey data"""
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        categories = []
        current_category = None
        current_question = None
        question_order = 0
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Detect section headers (categories)
            if self.is_section_header(line):
                # Save previous category
                if current_category:
                    if current_question:
                        current_category['questions'].append(current_question)
                    categories.append(current_category)
                
                category_name = self.clean_section_name(line)
                current_category = {
                    'name': category_name,
                    'description': f'Alumni Tracer Survey - {category_name}',
                    'order': len(categories),
                    'questions': []
                }
                question_order = 0
                current_question = None
                i += 1
                continue
            
            # Skip descriptive lines that aren't questions
            if (not current_category or 
                (line.startswith('Rate the relevance') and not line.endswith(':')) or
                (line.startswith('How useful are the following') and not line.endswith(':')) or
                ('Likert Scale' in line and not line.endswith(':'))):
                i += 1
                continue
            
            # Detect questions
            if self.is_question_line(line):
                # Save previous question
                if current_question:
                    current_category['questions'].append(current_question)
                
                question_text = self.clean_question_text(line)
                
                # Look ahead for options in the same line or next lines
                options = self.extract_options_from_line(line)
                
                # Check next lines for continuation or options
                j = i + 1
                while j < len(lines) and not self.is_question_line(lines[j]) and not self.is_section_header(lines[j]):
                    next_line = lines[j]
                    if self.is_option_line(next_line):
                        options.extend(self.extract_options_from_line(next_line))
                    elif not next_line.startswith('o '):
                        # Continuation of question text
                        question_text += ' ' + next_line.strip()
                    j += 1
                
                current_question = {
                    'question_text': question_text,
                    'question_type': self.determine_question_type(line, options),
                    'options': options,
                    'is_required': self.is_question_required(line),
                    'order': question_order,
                    'conditional_logic': self.extract_conditional_logic(line),
                    'help_text': self.extract_help_text(line),
                    'min_value': None,
                    'max_value': None
                }
                
                # Set rating scale values
                if current_question['question_type'] == 'rating':
                    current_question['min_value'] = 1
                    current_question['max_value'] = 5
                
                question_order += 1
                i = j - 1  # Skip processed lines
            
            # Handle sub-questions (indented with 'o ')
            elif line.startswith('o ') and current_category:
                sub_question_text = self.clean_question_text(line)
                options = self.extract_options_from_line(line)
                
                sub_question = {
                    'question_text': sub_question_text,
                    'question_type': self.determine_question_type(line, options),
                    'options': options,
                    'is_required': self.is_question_required(line),
                    'order': question_order,
                    'conditional_logic': self.extract_conditional_logic(line),
                    'help_text': self.extract_help_text(line),
                    'min_value': 1 if 'rating' in self.determine_question_type(line, options) else None,
                    'max_value': 5 if 'rating' in self.determine_question_type(line, options) else None
                }
                current_category['questions'].append(sub_question)
                question_order += 1
            
            i += 1
        
        # Add the last category and question
        if current_question and current_category:
            current_category['questions'].append(current_question)
        if current_category:
            categories.append(current_category)
        
        # Filter out empty categories
        categories = [cat for cat in categories if cat['questions']]
        
        return categories

    def is_section_header(self, line):
        """Detect if line is a section header"""
        return (line.startswith('SECTION') or 
                line.startswith('➤') or 
                re.match(r'^[A-Z][A-Za-z0-9\s]+:$', line))

    def clean_section_name(self, line):
        """Clean section name from header line"""
        name = re.sub(r'^SECTION \d+:\s*', '', line)
        name = re.sub(r'^➤\s*', '', name)
        name = name.rstrip(':').strip()
        return name[:100]  # Limit length for database

    def is_question_line(self, line):
        """Detect if line is a question"""
        return (line.startswith('•') or 
                line.startswith('o ') or
                ('?' in line and not line.startswith('☐')))

    def clean_question_text(self, line):
        """Clean question text"""
        text = re.sub(r'^[•o]\s*', '', line)
        # Remove option indicators but keep the question
        text = re.sub(r'\s*\([^)]*☐[^)]*\)', '', text)
        return text.strip()[:500]  # Limit length for database

    def determine_question_type(self, line, options=None):
        """Determine the appropriate question type based on content"""
        line_lower = line.lower()
        
        # Check for Likert scale and rating questions
        if ('likert' in line_lower or 
            '(1' in line or 
            'scale' in line_lower or
            'rate the' in line_lower or
            'how useful' in line_lower or
            'competitiveness' in line_lower):
            return 'rating'
        
        # If this is under a "Rate the relevance" or "Courses Usefulness" category context
        # and it's a simple skill/course name, it should be a rating
        if (len(line.split()) <= 3 and 
            not '?' in line and 
            not '☐' in line and
            any(keyword in line_lower for keyword in ['thinking', 'communication', 'innovation', 'collaboration', 
                                                     'leadership', 'productivity', 'entrepreneurship', 'citizenship',
                                                     'adaptability', 'education', 'courses', 'professional', 'electives',
                                                     'internship', 'ojt', 'curricular', 'activities'])):
            return 'rating'
        
        # Check for yes/no questions
        if ('☐ yes ☐ no' in line_lower or 
            '(yes/no)' in line_lower or
            line_lower.strip().endswith('? (☐ yes ☐ no)') or
            ('yes ☐ no' in line_lower and '☐' in line)):
            return 'yes_no'
        
        # Check for multiple choice with options
        if options and len(options) >= 2:
            return 'radio'
        
        # Check for multiple choice (radio buttons) based on checkbox symbols
        if '☐' in line and line.count('☐') >= 2:
            return 'radio'
        
        # Check for paragraph/long text
        if ('paragraph' in line_lower or 
            'recommendations' in line_lower or
            'feedback' in line_lower or
            'explain' in line_lower or
            'response)' in line_lower):
            return 'textarea'
        
        # Check for specific field types
        if ('income' in line_lower or 
            'salary' in line_lower or 
            'amount' in line_lower or
            '₱' in line):
            return 'radio'  # Income ranges are usually radio options
        
        if ('date' in line_lower or 
            'year' in line_lower):
            return 'number' if 'year' in line_lower else 'date'
        
        # Check for text fields that should be text inputs
        if any(word in line_lower for word in ['title', 'name', 'location', 'employer', 'occupation', 'agency']):
            return 'text'
        
        # Default to text input
        return 'text'

    def is_question_required(self, line):
        """Determine if question is required (basic heuristic)"""
        # Most tracer survey questions are typically required
        return True

    def extract_conditional_logic(self, line):
        """Extract conditional logic information"""
        logic = {}
        line_lower = line.lower()
        
        if 'if yes' in line_lower:
            logic['depends_on_value'] = 'Yes'
            logic['condition_text'] = 'Show if previous question is Yes'
        elif 'if no' in line_lower:
            logic['depends_on_value'] = 'No'
            logic['condition_text'] = 'Show if previous question is No'
        
        return logic if logic else None

    def extract_help_text(self, line):
        """Extract help text from parentheses or additional context"""
        # Look for text in parentheses that's not options
        match = re.search(r'\(([^☐][^)]+)\)', line)
        if match:
            help_text = match.group(1).strip()
            if not help_text.startswith('☐'):
                return help_text[:500]
        return ''

    def is_option_line(self, line):
        """Check if line contains options"""
        return '☐' in line and not self.is_question_line(line)

    def extract_options_from_line(self, line):
        """Extract all options from a line containing checkboxes"""
        options = []
        # Extract all options from the line using regex
        matches = re.findall(r'☐\s*([^☐\n]+)', line)
        for match in matches:
            option = match.strip()
            # Clean up option text
            option = re.sub(r'\s*\).*$', '', option)  # Remove closing parentheses and everything after
            option = re.sub(r'–.*$', '', option)  # Remove dashes and everything after (for ranges)
            if option and option not in ['', ' ']:
                options.append(option.strip())
        return options

    def clean_option_text(self, line):
        """Clean option text - deprecated, use extract_options_from_line instead"""
        return self.extract_options_from_line(line)

    def is_sub_question(self, line):
        """Check if line is a sub-question"""
        return line.startswith('o ') and '?' in line

    def show_dry_run_preview(self, parsed_data):
        """Show what would be created in dry run mode"""
        self.stdout.write(self.style.SUCCESS('=== DRY RUN PREVIEW ==='))
        
        total_questions = sum(len(cat['questions']) for cat in parsed_data)
        self.stdout.write(f'Would create {len(parsed_data)} categories with {total_questions} total questions:\n')
        
        for category in parsed_data:
            self.stdout.write(self.style.SUCCESS(f"📁 Category: {category['name']}"))
            self.stdout.write(f"   Description: {category['description']}")
            self.stdout.write(f"   Questions: {len(category['questions'])}\n")
            
            for i, question in enumerate(category['questions'][:3]):  # Show first 3 questions
                self.stdout.write(f"   ❓ Q{i+1}: {question['question_text'][:80]}...")
                self.stdout.write(f"      Type: {question['question_type']}")
                if question['options']:
                    self.stdout.write(f"      Options: {len(question['options'])} choices")
                if question['conditional_logic']:
                    self.stdout.write(f"      Conditional: {question['conditional_logic']}")
                self.stdout.write("")
            
            if len(category['questions']) > 3:
                self.stdout.write(f"   ... and {len(category['questions']) - 3} more questions\n")
        
        self.stdout.write(self.style.WARNING('Run without --dry-run to actually create the survey structure.'))

    def create_survey_structure(self, parsed_data, admin_user):
        """Create the actual survey structure in the database"""
        created_categories = 0
        created_questions = 0
        conditional_questions = []  # Track questions with conditional logic
        
        self.stdout.write(self.style.SUCCESS('Creating survey structure...'))
        
        for category_data in parsed_data:
            # Create category
            category, created = SurveyCategory.objects.get_or_create(
                name=category_data['name'],
                defaults={
                    'description': category_data['description'],
                    'order': category_data['order'],
                    'is_active': True,
                    'created_by': admin_user
                }
            )
            
            if created:
                created_categories += 1
                self.stdout.write(f"✅ Created category: {category.name}")
            else:
                self.stdout.write(f"📁 Category exists: {category.name}")
            
            # Create questions for this category
            previous_question = None
            for question_data in category_data['questions']:
                question_kwargs = {
                    'category': category,
                    'question_text': question_data['question_text'],
                    'question_type': question_data['question_type'],
                    'options': question_data['options'] if question_data['options'] else None,
                    'is_required': question_data['is_required'],
                    'order': question_data['order'],
                    'help_text': question_data['help_text'],
                    'is_active': True,
                    'created_by': admin_user
                }
                
                # Handle rating questions
                if question_data['question_type'] == 'rating':
                    question_kwargs['min_value'] = 1
                    question_kwargs['max_value'] = 5
                
                # Create the question
                question, created = SurveyQuestion.objects.get_or_create(
                    category=category,
                    question_text=question_data['question_text'],
                    defaults=question_kwargs
                )
                
                if created:
                    created_questions += 1
                    self.stdout.write(f"  ✅ Created question: {question.question_text[:50]}...")
                    
                    # Handle conditional logic
                    if question_data['conditional_logic'] and previous_question:
                        conditional_questions.append({
                            'question': question,
                            'depends_on': previous_question,
                            'logic': question_data['conditional_logic']
                        })
                else:
                    self.stdout.write(f"  📝 Question exists: {question.question_text[:50]}...")
                
                previous_question = question
        
        # Set up conditional logic after all questions are created
        self.setup_conditional_logic(conditional_questions)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 Survey population completed!\n'
                f'Created: {created_categories} categories, {created_questions} questions\n'
                f'Total: {SurveyCategory.objects.count()} categories, {SurveyQuestion.objects.count()} questions\n'
                f'Conditional questions: {len(conditional_questions)}\n\n'
                f'✅ Your Alumni Tracer Survey is now available in the Survey Management system!\n'
                f'📊 Access it through the SuperAdmin or Admin dashboard -> Survey Management\n'
                f'🔗 The survey includes proper conditional logic and question types\n'
                f'📝 No existing survey management code was modified - only new data was added'
            )
        )

    def setup_conditional_logic(self, conditional_questions):
        """Set up conditional logic for questions"""
        for item in conditional_questions:
            question = item['question']
            depends_on = item['depends_on']
            logic = item['logic']
            
            question.depends_on_question = depends_on
            question.depends_on_value = logic.get('depends_on_value', 'Yes')
            question.save()
            
            self.stdout.write(f"  🔗 Set conditional: {question.question_text[:30]}... depends on {depends_on.question_text[:30]}...")
