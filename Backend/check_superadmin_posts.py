import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from posts_app.models import Post

User = get_user_model()

# Find super admin users
super_admins = User.objects.filter(is_superuser=True)
print('=== SUPER ADMIN USERS ===')
for user in super_admins:
    print(f'ID: {user.id} | Email: {user.email} | Name: {user.first_name} {user.last_name}')
print()

# Find posts by super admins
super_admin_posts = Post.objects.filter(user__is_superuser=True)
print(f'=== POSTS BY SUPER ADMINS ({super_admin_posts.count()} total) ===')
for post in super_admin_posts:
    title = post.title[:50] if post.title else '(No title)'
    print(f'Post ID: {post.id} | User: {post.user.email} | Title: {title}... | Created: {post.created_at}')
print()

# Check admin (non-superuser) posts
admin_posts = Post.objects.filter(user__is_staff=True, user__is_superuser=False)
print(f'=== POSTS BY REGULAR ADMINS ({admin_posts.count()} total) ===')
for post in admin_posts[:5]:
    title = post.title[:50] if post.title else '(No title)'
    print(f'Post ID: {post.id} | User: {post.user.email} | Title: {title}...')
