import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from posts_app.models import Post

User = get_user_model()

# Find posts by super admins
super_admin_posts = Post.objects.filter(user__is_superuser=True)

print('=== POSTS TO BE DELETED ===')
for post in super_admin_posts:
    title = post.title[:50] if post.title else '(No title)'
    print(f'Post ID: {post.id} | User: {post.user.email} | Title: {title}')
    print(f'   Created: {post.created_at}')
    print(f'   Comments: {post.comments_count} | Likes: {post.likes_count}')
    print()

if super_admin_posts.exists():
    count = super_admin_posts.count()
    print(f'\n⚠️  About to delete {count} post(s) by super admin users...')
    
    # Delete the posts
    deleted_count, deleted_details = super_admin_posts.delete()
    
    print(f'✅ Successfully deleted {deleted_count} records:')
    for model, count in deleted_details.items():
        if count > 0:
            print(f'   - {model}: {count}')
    print()
    print('Super admin posts have been removed!')
else:
    print('No posts by super admins found.')
