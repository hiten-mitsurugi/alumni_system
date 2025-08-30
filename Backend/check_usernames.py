import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
django.setup()

from auth_app.models import CustomUser

users = CustomUser.objects.all()[:5]
for user in users:
    print(f"ID: {user.id}, Username: '{user.username}', Email: '{user.email}'")
