# Username Generation Utility
from django.contrib.auth import get_user_model
import re
from django.db import transaction

def generate_username_from_name(first_name, last_name):
    """
    Generate a clean username from first_name and last_name only.
    Format: firstname-lastname (lowercase, no spaces, alphanumeric + hyphens only)
    """
    # Combine names (only first and last)
    full_name = f"{first_name} {last_name}"
    
    # Clean the name: lowercase, remove special characters, replace spaces with hyphens
    clean_name = re.sub(r'[^a-zA-Z0-9\s]', '', full_name.lower())
    username = re.sub(r'\s+', '-', clean_name.strip())
    
    return username

def generate_unique_username(first_name, last_name):
    """
    Generate a unique username by appending numbers if needed.
    """
    User = get_user_model()
    base_username = generate_username_from_name(first_name, last_name)
    
    username = base_username
    counter = 1
    
    # Check if username exists and add number if needed
    while User.objects.filter(username=username).exists():
        username = f"{base_username}-{counter}"
        counter += 1
    
    return username

def update_existing_usernames():
    """
    Update all existing users to have name-based usernames instead of emails.
    """
    User = get_user_model()
    
    with transaction.atomic():
        users = User.objects.all()
        
        for user in users:
            if '@' in user.username:  # Only update email-based usernames
                new_username = generate_unique_username(
                    user.first_name, 
                    user.last_name
                )
                print(f"Updating {user.username} -> {new_username}")
                user.username = new_username
                user.save()
        
        print(f"Updated {len([u for u in users if '@' in u.username])} usernames")

if __name__ == "__main__":
    # Test the function
    print(generate_username_from_name("Roman", "Osorio"))  # roman-osorio
    print(generate_username_from_name("María José", "García López"))  # maria-jose-garcia-lopez
    print(generate_username_from_name("John", "O'Connor"))  # john-oconnor
