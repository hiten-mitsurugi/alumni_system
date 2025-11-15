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
        """Parse tracer.txt content into structured survey data with enhanced logic"""
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        categories = []
        current_category = None
        current_question = None
        question_order = 0
        likert_context = False  # Track if we're in a Likert scale section
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Detect major section headers (SECTION X:)
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
                likert_context = False
                i += 1
                continue
            
            # Detect subsection headers (➤ SubName) - create as separate categories
            elif self.is_subsection_header(line):
                # Save previous question and category
                if current_question and current_category:
                    current_category['questions'].append(current_question)
                    current_question = None
                if current_category:
                    categories.append(current_category)
                
                # Create subsection as separate category
                subsection_name = self.clean_section_name(line)
                
                # Special handling for specific subsections
                if 'courses usefulness' in subsection_name.lower():
                    subsection_name = "Courses Usefulness"
                elif 'programs usefulness' in subsection_name.lower():
                    subsection_name = "Programs Usefulness"
                elif 'likert scale' in subsection_name.lower():
                    # Extract parent section name for better context
                    if categories and ('skills' in categories[-1]['name'].lower() or 'workplace' in categories[-1]['name'].lower()):
                        subsection_name = "Skills Relevance in Workplace"
                    else:
                        subsection_name = "Likert Scale Assessment"
                
                current_category = {
                    'name': subsection_name[:100],
                    'description': f'Alumni Tracer Survey - {subsection_name}',
                    'order': len(categories),
                    'questions': []
                }
                question_order = 0
                likert_context = True
                
                i += 1
                continue
            
            # Detect context lines (instructions, not questions)
            elif self.is_context_line(line):
                if 'likert' in line.lower():
                    likert_context = True
                i += 1
                continue
            
            # Skip pure descriptive lines
            elif (not current_category or 
                  line.startswith('Rate the relevance') or
                  line.startswith('How useful are the following')):
                i += 1
                continue
            
            # Detect questions
            elif self.is_question_line(line):
                # Save previous question
                if current_question:
                    current_category['questions'].append(current_question)
                
                question_text = self.clean_question_text(line)
                
                # Look ahead for options and continuation
                options = self.extract_options_from_line(line)
                
                # Check next lines for continuation or additional options
                j = i + 1
                while j < len(lines) and not self.is_question_line(lines[j]) and not self.is_section_header(lines[j]) and not self.is_subsection_header(lines[j]):
                    next_line = lines[j]
                    if self.is_option_line(next_line):
                        additional_options = self.extract_options_from_line(next_line)
                        options.extend(additional_options)
                    elif not next_line.startswith('o ') and not self.is_context_line(next_line):
                        # Continuation of question text (but avoid context lines)
                        question_text += ' ' + next_line.strip()
                    j += 1
                
                # Determine question type with context awareness
                question_type = self.determine_question_type(line, options)
                
                # Override for Likert context - if we're in a Likert section and it's a simple item
                if (likert_context and not options and not '?' in line and 
                    len(line.split()) <= 5 and not any(word in line.lower() for word in ['title', 'name', 'location'])):
                    question_type = 'rating'
                
                # Also check if the category name suggests rating
                if (current_category and 'usefulness' in current_category.get('name', '').lower() and 
                    not options and not '?' in line):
                    question_type = 'rating'
                
                current_question = {
                    'question_text': question_text,
                    'question_type': question_type,
                    'options': options if options else None,
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
                    'options': options if options else None,
                    'is_required': self.is_question_required(line),
                    'order': question_order,
                    'conditional_logic': self.extract_conditional_logic(line),
                    'help_text': self.extract_help_text(line),
                    'min_value': 1 if self.determine_question_type(line, options) == 'rating' else None,
                    'max_value': 5 if self.determine_question_type(line, options) == 'rating' else None
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
        """Detect if line is a major section header (SECTION X: or major ➤ topics)"""
        # Explicit SECTION headers
        if line.startswith('SECTION') and ':' in line:
            return True
        
        # Major topic headers with ➤ that should be categories
        major_topics = [
            'Present Employment',
            'First Job',
            'Skills Relevance in Workplace',
            'Curriculum and Program Relevance',
            'Perception and Further Studies',
            'Feedback and Recommendations'
        ]
        
        if line.startswith('➤'):
            for topic in major_topics:
                if topic.lower() in line.lower():
                    return True
        
        return False

    def is_subsection_header(self, line):
        """Detect if line is a subsection header (➤ SubName that's not a major section)"""
        if not line.startswith('➤'):
            return False
        
        # Skip if it's a major section
        if self.is_section_header(line):
            return False
        
        # These are subsections within major sections
        subsection_indicators = [
            'Likert Scale',
            'Courses Usefulness', 
            'Programs Usefulness'
        ]
        
        for indicator in subsection_indicators:
            if indicator.lower() in line.lower():
                return True
        
        return False

    def is_context_line(self, line):
        """Detect if line is context/instruction (not a question)"""
        context_patterns = [
            'Rate the relevance',
            'How useful are the following course curricula',
            'How useful are the following curricular programs',
            '➤ Likert Scale',
            'Likert Scale',
            'If yes:'
        ]
        return any(pattern in line for pattern in context_patterns)

    def clean_section_name(self, line):
        """Clean section name from header line"""
        name = line
        
        # Remove SECTION X: prefix
        name = re.sub(r'^SECTION \d+:\s*', '', name)
        
        # Remove ➤ prefix
        name = re.sub(r'^➤\s*', '', name)
        
        # Remove trailing colons and clean up
        name = name.rstrip(':').strip()
        
        # Remove conditional notes in parentheses
        name = re.sub(r'\s*\([^)]*if\s+[^)]*\)', '', name)
        
        return name[:100]  # Limit length for database

    def is_question_line(self, line):
        """Detect if line is a question"""
        return (line.startswith('•') or 
                line.startswith('o ') or
                ('?' in line and not line.startswith('☐')))

    def clean_question_text(self, line):
        """Clean question text - remove all option-related content in parentheses but keep helpful examples"""
        text = re.sub(r'^[•o]\s*', '', line)
        
        # Remove option-related content in parentheses (dropdown, checkboxes, conditional logic)
        text = re.sub(r'\s*\([^)]*(?:Drop\s*down|☐|Required|if\s+yes|if\s+no|before\s+shown)[^)]*\)', '', text, flags=re.IGNORECASE)
        
        # Keep helpful examples but clean them up - keep (e.g., ...) patterns
        # No removal needed for (e.g., ...) as they are helpful context
        
        # Remove any remaining empty parentheses or orphaned closing parentheses  
        text = re.sub(r'\s*\(\s*\)', '', text)
        text = re.sub(r'(?<!\w)\)\s*', '', text)  # Remove orphaned ) not preceded by word
        text = re.sub(r'\s*\(\s*(?!\w)', '', text)  # Remove orphaned ( not followed by word
        
        # Clean up extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text)
        
        # Remove trailing punctuation except question marks
        text = re.sub(r'[^\w\s?)]+$', '', text)
        
        return text.strip()[:500]  # Limit length for database

    def determine_question_type(self, line, options=None):
        """Determine the appropriate question type based on content with enhanced detection"""
        line_lower = line.lower()
        
        # 1. Text input fields - CHECK THIS FIRST to avoid false positives
        if any(word in line_lower for word in ['title', 'name', 'location', 'employer', 'occupation', 'agency', 'field', 'specialization']):
            return 'text'
        
        # 2. Explicit dropdown detection - use 'select' type for dropdown
        if 'drop down' in line_lower or 'dropdown' in line_lower:
            return 'select'  # Use 'select' type for dropdown questions
        
        # 3. Income questions with options but no explicit dropdown keyword
        if 'income' in line_lower and options and len(options) > 2:
            return 'select'  # Income questions with multiple options should be dropdown
        
        # 4. Yes/No questions - distinguish between 2-option and 3-option
        checkbox_count = line.count('☐')
        yes_no_patterns = ['☐ yes ☐ no', '(yes/no)', 'yes ☐ no']
        
        # Special case: "Are you presently employed?" should be yes_no even with 3 options
        if 'are you presently employed' in line_lower:
            return 'yes_no'
        
        if any(pattern in line_lower for pattern in yes_no_patterns):
            if checkbox_count == 2:
                return 'yes_no'  # Pure yes/no with 2 options
            elif checkbox_count == 3:
                return 'radio'   # Yes/No/Other (like "Never been employed") with 3 options
        
        # 5. Multiple checkbox detection (allows multiple selections)
        if checkbox_count > 3:
            return 'checkbox'  # Multiple selection allowed for 4+ options
        
        # 6. Likert scale and rating questions
        if ('likert' in line_lower or 
            '(1' in line or 
            'scale' in line_lower or
            'rate the' in line_lower or
            'how useful' in line_lower or
            'competitiveness' in line_lower):
            return 'rating'
        
        # 7. Simple skill/course names in rating context (heuristic)
        if (len(line.split()) <= 4 and 
            not '?' in line and 
            not '☐' in line and
            any(keyword in line_lower for keyword in ['thinking', 'communication', 'innovation', 'collaboration', 
                                                     'leadership', 'productivity', 'entrepreneurship', 'citizenship',
                                                     'adaptability', 'education', 'courses', 'professional', 'electives',
                                                     'internship', 'ojt', 'curricular', 'activities'])):
            return 'rating'
        
        # 8. Multiple choice with extracted options (3+ options = radio, 2 options = check context)
        if options and len(options) >= 3:
            return 'radio'
        elif options and len(options) == 2:
            # Check if it's a yes/no pattern
            if any(pattern in line_lower for pattern in yes_no_patterns):
                return 'yes_no'
            else:
                return 'radio'
        
        # 9. Standard multiple choice based on checkbox symbols (3 or fewer options)
        if '☐' in line and checkbox_count >= 2:
            return 'radio'
        
        # 10. Paragraph/long text responses
        if ('paragraph' in line_lower or 
            'recommendations' in line_lower or
            'feedback' in line_lower or
            'explain' in line_lower or
            'response)' in line_lower):
            return 'textarea'
        
        # 11. Income/salary fields (usually dropdowns with ranges)
        if ('income' in line_lower or 
            'salary' in line_lower or 
            'amount' in line_lower or
            '₱' in line):
            return 'radio'
        
        # 12. Date/year fields
        if ('date' in line_lower or 
            'year' in line_lower):
            return 'number' if 'year' in line_lower else 'date'
        

        # Default to text input
        return 'text'

    def is_question_required(self, line):
        """Determine if question is required (basic heuristic)"""
        # Most tracer survey questions are typically required
        return True

    def extract_conditional_logic(self, line):
        """Extract conditional logic information with enhanced parsing"""
        logic = {}
        line_lower = line.lower()
        original_line = line
        
        # Pattern 1: Informal logic (if yes show, if no do no show)
        if 'if yes show' in line_lower:
            logic['depends_on_value'] = 'Yes'
            logic['condition_text'] = 'Show if previous question is Yes'
        elif 'if no show' in line_lower:
            logic['depends_on_value'] = 'No'
            logic['condition_text'] = 'Show if previous question is No'
        elif 'if yes' in line_lower and 'show' in line_lower:
            logic['depends_on_value'] = 'Yes'
            logic['condition_text'] = 'Show if previous question is Yes'
        
        # Pattern 2: Formal logic (Required "VALUE" answer from "QUESTION")
        formal_pattern = r'Required\s*"([^"]+)"\s*answer\s*from\s*"([^"]+)"\s*before\s*shown'
        formal_match = re.search(formal_pattern, original_line, re.IGNORECASE)
        if formal_match:
            required_value = formal_match.group(1)
            question_name = formal_match.group(2)
            logic['depends_on_value'] = required_value
            logic['depends_on_question_name'] = question_name
            logic['condition_text'] = f'Show if "{question_name}" = "{required_value}"'
        
        # Pattern 3: Complex dependencies (store for manual handling)
        if 'and' in line_lower and ('required' in line_lower or 'before shown' in line_lower):
            logic['complex_dependency'] = True
            logic['condition_text'] = f'Complex condition: {original_line}'
        
        return logic if logic else None

    def extract_help_text(self, line):
        """Extract help text from parentheses or additional context"""
        # Return empty string - user wants help text to be blank
        return ''

    def is_option_line(self, line):
        """Check if line contains options"""
        return '☐' in line and not self.is_question_line(line)

    def extract_options_from_line(self, line):
        """Extract all options from a line with enhanced parsing for multiple formats"""
        options = []
        
        # Format 1: Dropdown options in parentheses - "Drop down(Option1, Option2, ...)" or "Dropdown(Option1, Option2, ...)"
        dropdown_patterns = [
            r'[Dd]rop\s*[Dd]own\s*\(\s*([^)]+)\s*\)',
            r'[Dd]ropdown\s*\(\s*([^)]+)\s*\)'
        ]
        
        for pattern in dropdown_patterns:
            dropdown_match = re.search(pattern, line)
            if dropdown_match:
                options_text = dropdown_match.group(1)
                # Check if it uses pipe separator (for income questions) or comma separator
                separator = '|' if '|' in options_text else ','
                # Split by the appropriate separator and clean each option
                for option in options_text.split(separator):
                    clean_option = option.strip()
                    # Remove leading/trailing punctuation and whitespace
                    clean_option = re.sub(r'^[\s,|]+|[\s,|)]+$', '', clean_option)
                    if clean_option and clean_option not in ['', ' ']:
                        options.append(clean_option)
                break  # Found dropdown options, don't process other formats
        
        # Format 2: Income options in parentheses without "Drop down" keyword
        # Example: "Monthly Income in First Job ( Less than ₱15,000|  ₱15,000 – ₱29,999| ...)"
        if not options and 'income' in line.lower():
            income_pattern = r'\(\s*([^)]*₱[^)]+)\s*\)'
            income_match = re.search(income_pattern, line)
            if income_match:
                options_text = income_match.group(1)
                # Check if it uses pipe separator (new format) or comma separator (old format)
                separator = '|' if '|' in options_text else ','
                # Split by the appropriate separator and clean each option
                for option in options_text.split(separator):
                    clean_option = option.strip()
                    # Remove leading/trailing punctuation and whitespace
                    clean_option = re.sub(r'^[\s,|]+|[\s,|)]+$', '', clean_option)
                    if clean_option and clean_option not in ['', ' ']:
                        options.append(clean_option)
        
        # If no dropdown or income options found, check for checkbox options
        if not options:
            # Format 3: Checkbox options - "☐ Option1 ☐ Option2 ☐ Option3"
            checkbox_matches = re.findall(r'☐\s*([^☐\n)]+)', line)
            for match in checkbox_matches:
                option = match.strip()
                # Clean up option text - remove trailing punctuation and parentheses
                option = re.sub(r'\s*[),\.].*$', '', option)  # Remove ) or , and everything after
                option = re.sub(r'–.*$', '', option)  # Remove dashes and everything after (for ranges)
                option = re.sub(r'\s+', ' ', option)  # Normalize whitespace
                if option and option not in ['', ' '] and option not in options:
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
        """Create the actual survey structure in the database with enhanced logic"""
        created_categories = 0
        created_questions = 0
        conditional_questions = []  # Track questions with conditional logic
        all_questions = {}  # Map question text to question object for complex lookups
        
        self.stdout.write(self.style.SUCCESS('Creating survey structure...'))
        
        for category_data in parsed_data:
            # Create category
            category, created = SurveyCategory.objects.get_or_create(
                name=category_data['name'],
                defaults={
                    'description': category_data['description'],
                    'order': category_data['order'],
                    'is_active': True,
                    'include_in_registration': False,  # Tracer categories should NOT appear in registration
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
                else:
                    self.stdout.write(f"  📝 Question exists: {question.question_text[:50]}...")
                
                # Store question for lookups
                all_questions[question.question_text] = question
                
                # Handle conditional logic
                if question_data['conditional_logic']:
                    conditional_questions.append({
                        'question': question,
                        'depends_on': previous_question,
                        'logic': question_data['conditional_logic']
                    })
                
                previous_question = question
        
        # Set up conditional logic after all questions are created
        self.setup_conditional_logic(conditional_questions, all_questions)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 Enhanced Survey population completed!\n'
                f'Created: {created_categories} categories, {created_questions} questions\n'
                f'Total: {SurveyCategory.objects.count()} categories, {SurveyQuestion.objects.count()} questions\n'
                f'Conditional questions: {len(conditional_questions)}\n\n'
                f'✅ Your Alumni Tracer Survey is now available!\n'
                f'📊 Enhanced parsing with:\n'
                f'   • Proper subsection handling\n'
                f'   • Improved option extraction\n'
                f'   • Enhanced conditional logic detection\n'
                f'   • Better question type identification\n'
                f'� The survey includes smart conditional logic and question types\n'
            )
        )

    def setup_conditional_logic(self, conditional_questions, all_questions):
        """Set up conditional logic for questions with enhanced lookups"""
        for item in conditional_questions:
            question = item['question']
            logic = item['logic']
            
            # Handle named question dependencies (formal logic)
            if logic.get('depends_on_question_name'):
                question_name = logic['depends_on_question_name']
                # Try to find the question by exact name match
                depends_on_question = None
                for q_text, q_obj in all_questions.items():
                    if question_name.lower() in q_text.lower() or q_text.lower() in question_name.lower():
                        depends_on_question = q_obj
                        break
                
                if depends_on_question:
                    question.depends_on_question = depends_on_question
                    question.depends_on_value = logic.get('depends_on_value', 'Yes')
                    self.stdout.write(f"  🔗 Named dependency: {question.question_text[:30]}... depends on {depends_on_question.question_text[:30]}...")
                else:
                    # Store dependency information in help_text for manual review
                    dependency_info = f" [DEPENDENCY: Requires '{logic['depends_on_value']}' from '{question_name}']"
                    question.help_text = (question.help_text + dependency_info)[:500]
                    self.stdout.write(f"  ⚠️  Complex dependency stored in help_text: {question.question_text[:30]}...")
            
            # Handle simple previous question dependencies
            elif item.get('depends_on'):
                depends_on = item['depends_on']
                question.depends_on_question = depends_on
                question.depends_on_value = logic.get('depends_on_value', 'Yes')
                self.stdout.write(f"  🔗 Simple dependency: {question.question_text[:30]}... depends on {depends_on.question_text[:30]}...")
            
            # Handle complex dependencies (store in help_text for review)
            elif logic.get('complex_dependency'):
                complex_info = f" [COMPLEX: {logic['condition_text'][:200]}]"
                question.help_text = (question.help_text + complex_info)[:500]
                self.stdout.write(f"  🔄 Complex dependency noted: {question.question_text[:30]}...")
            
            question.save()
