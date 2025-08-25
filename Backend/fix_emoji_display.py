#!/usr/bin/env python
"""
Fix emoji display issues by updating reaction types directly
"""
import os
import sys
import django
from django.conf import settings

# Add the Backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
django.setup()

from posts_app.models import Reaction

def fix_emoji_display():
    print("🔧 Fixing emoji display issues...")
    
    # Check current reaction types
    print("\nCurrent REACTION_TYPES:")
    for reaction_type, emoji in Reaction.REACTION_TYPES:
        print(f"  {reaction_type}: {emoji}")
    
    # The issue is that we need to ensure the frontend and backend emojis match
    # Let's print what we have in the database
    print("\nReactions in database:")
    reactions = Reaction.objects.all()
    for reaction in reactions:
        try:
            emoji = reaction.emoji
            print(f"  {reaction.reaction_type}: {emoji}")
        except KeyError as e:
            print(f"  {reaction.reaction_type}: ERROR - {e}")
    
    print("\nNo database changes needed - the issue is likely in the frontend/backend emoji mismatch")
    print("Frontend should use the same emojis as backend:")
    
    backend_emojis = {
        'like': '👍',
        'love': '❤️', 
        'laugh': '😄',
        'wow': '😮',
        'sad': '😢',
        'angry': '😡'
    }
    
    print("\nBackend emojis (original Facebook style):")
    for reaction_type, emoji in backend_emojis.items():
        print(f"  {reaction_type}: {emoji}")

if __name__ == '__main__':
    fix_emoji_display()
