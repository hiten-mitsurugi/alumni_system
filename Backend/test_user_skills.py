"""
Test script to verify UserSkill functionality works correctly.
"""
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
django.setup()

from auth_app.models import CustomUser, UserSkill
from django.contrib.auth import get_user_model

def test_user_skill_functionality():
    """Test the UserSkill model and functionality"""
    
    print("🧪 Testing UserSkill Functionality")
    print("=" * 50)
    
    User = get_user_model()
    
    # Create or get test user
    user, created = User.objects.get_or_create(
        username='test_skill_user',
        defaults={
            'email': 'testskill@example.com',
            'first_name': 'Test',
            'last_name': 'Skills',
            'is_approved': True
        }
    )
    
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"✅ Created test user: {user.username}")
    else:
        print(f"✅ Using existing test user: {user.username}")
    
    # Clear existing skills for clean test
    UserSkill.objects.filter(user=user).delete()
    
    # Test 1: Create skills in different categories
    print("\n1️⃣ Creating skills in different categories...")
    
    skills_data = [
        {
            'name': 'Python',
            'category': 'technical',
            'proficiency': 'advanced',
            'description': 'Web development with Django, data analysis with pandas'
        },
        {
            'name': 'JavaScript',
            'category': 'technical',
            'proficiency': 'intermediate',
            'description': 'Frontend development with Vue.js and React'
        },
        {
            'name': 'Leadership',
            'category': 'soft_skills',
            'proficiency': 'advanced',
            'description': 'Led teams of 5+ developers, managed project timelines'
        },
        {
            'name': 'Spanish',
            'category': 'languages',
            'proficiency': 'intermediate',
            'description': 'Conversational level, can handle business meetings'
        },
        {
            'name': 'Docker',
            'category': 'tools',
            'proficiency': 'beginner',
            'description': 'Basic containerization for development environments'
        }
    ]
    
    created_skills = []
    for skill_data in skills_data:
        skill = UserSkill.objects.create(user=user, **skill_data)
        created_skills.append(skill)
        print(f"   ✅ Created: {skill.name} ({skill.category}) - {skill.proficiency}")
    
    # Test 2: Test unique constraint
    print("\n2️⃣ Testing unique constraint (same skill in same category)...")
    
    try:
        # Try to create duplicate skill in same category
        duplicate_skill = UserSkill.objects.create(
            user=user,
            name='Python',
            category='technical',
            proficiency='expert'
        )
        print("   ❌ Duplicate skill created (this shouldn't happen)")
    except Exception as e:
        print(f"   ✅ Unique constraint working: {e}")
    
    # Test 3: Test ordering
    print("\n3️⃣ Testing skill ordering...")
    
    user_skills = UserSkill.objects.filter(user=user).order_by('category', 'name')
    print("   Skills ordered by category, then name:")
    for skill in user_skills:
        print(f"   - {skill.category}: {skill.name} ({skill.proficiency})")
    
    # Test 4: Test categorization
    print("\n4️⃣ Testing skill categorization...")
    
    categories = {}
    for skill in user_skills:
        if skill.category not in categories:
            categories[skill.category] = []
        categories[skill.category].append(skill)
    
    print("   Skills by category:")
    for category, skills in categories.items():
        print(f"   📂 {category.title()}:")
        for skill in skills:
            print(f"      - {skill.name} ({skill.proficiency})")
    
    # Test 5: Test model methods
    print("\n5️⃣ Testing model string representations...")
    
    for skill in created_skills[:3]:  # Test first 3 skills
        print(f"   {skill}")  # This calls __str__ method
    
    # Test 6: Test filtering and queries
    print("\n6️⃣ Testing queries and filtering...")
    
    # Find technical skills
    technical_skills = UserSkill.objects.filter(user=user, category='technical')
    print(f"   Technical skills: {technical_skills.count()}")
    
    # Find advanced proficiency skills
    advanced_skills = UserSkill.objects.filter(user=user, proficiency='advanced')
    print(f"   Advanced skills: {advanced_skills.count()}")
    
    # Find skills with descriptions
    described_skills = UserSkill.objects.filter(user=user, description__isnull=False)
    print(f"   Skills with descriptions: {described_skills.count()}")
    
    print("\n" + "=" * 50)
    print("🎉 UserSkill Test Complete!")
    print(f"📊 Total skills created: {UserSkill.objects.filter(user=user).count()}")
    print(f"📊 Categories represented: {len(categories)}")

if __name__ == "__main__":
    test_user_skill_functionality()