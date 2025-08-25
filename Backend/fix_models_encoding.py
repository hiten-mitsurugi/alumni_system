#!/usr/bin/env python
"""
Script to update the reaction types directly in the code using UTF-8 encoding
"""
import os
import sys

def fix_models_file():
    models_path = r"c:\Users\USER\OneDrive\Desktop\Proejct\Thesis Merge\main\Backend\posts_app\models.py"
    
    # Read the current file
    with open(models_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace the reaction types section
    old_reaction_types = """    REACTION_TYPES = (
        ('like', '👍'),
        ('applaud', '👏'),
        ('heart', '❤️'),
        ('support', '🤝'),
        ('laugh', '�'),
        ('sad', '�'),
    )"""
    
    new_reaction_types = """    REACTION_TYPES = (
        ('like', '👍'),
        ('applaud', '👏'),
        ('heart', '❤️'),
        ('support', '🤝'),
        ('laugh', '😂'),
        ('sad', '😢'),
    )"""
    
    # Update content
    content = content.replace(old_reaction_types, new_reaction_types)
    
    # Write back with UTF-8 encoding
    with open(models_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Updated models.py with proper UTF-8 emojis")
    print("New reaction types:")
    print("  like: 👍")
    print("  applaud: 👏") 
    print("  heart: ❤️")
    print("  support: 🤝")
    print("  laugh: 😂")
    print("  sad: 😢")

if __name__ == '__main__':
    fix_models_file()
