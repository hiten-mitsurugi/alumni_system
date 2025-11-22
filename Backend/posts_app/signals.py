from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from .models import Comment, Reaction
from notifications_app.utils import create_notification
import re

User = get_user_model()


# ========================================
# Comment Notification Handlers
# ========================================

def notify_post_author_on_comment(comment):
    """
    Notify post author when someone comments on their post.
    Skips if user is commenting on their own post.
    """
    if comment.post.user != comment.user:
        create_notification(
            user=comment.post.user,
            actor=comment.user,
            notification_type='post',
            title='New Comment',
            message=f"{comment.user.first_name} {comment.user.last_name} commented on your post",
            link_route='/alumni/home',
            link_params={'postId': comment.post.id},
            metadata={'comment_id': comment.id}
        )


def notify_parent_comment_author_on_reply(comment):
    """
    Notify parent comment author when someone replies to their comment.
    Skips if user is replying to their own comment.
    """
    if comment.parent and comment.parent.user != comment.user:
        create_notification(
            user=comment.parent.user,
            actor=comment.user,
            notification_type='post',
            title='New Reply',
            message=f"{comment.user.first_name} {comment.user.last_name} replied to your comment",
            link_route='/alumni/home',
            link_params={'postId': comment.post.id},
            metadata={'comment_id': comment.id, 'parent_comment_id': comment.parent.id}
        )


def detect_and_notify_mentions(comment):
    """
    Detect @mentions in comment content and notify mentioned users.
    Pattern: @[User Name](user_id)
    Skips if user mentions themselves.
    """
    print(f"🔍 SIGNAL: Checking mentions in comment {comment.id} by user {comment.user.id}")
    print(f"🔍 SIGNAL: Comment content: {comment.content[:100]}")
    
    mention_pattern = r'@\[([^\]]+)\]\((\d+)\)'
    matches = re.findall(mention_pattern, comment.content)
    
    print(f"🔍 SIGNAL: Found {len(matches)} mentions: {matches}")
    
    if not matches:
        return
    
    # Track notified users to avoid duplicates
    notified_user_ids = set()
    
    for name, user_id in matches:
        # Skip if already notified this user
        if user_id in notified_user_ids:
            continue
            
        try:
            mentioned_user = User.objects.get(id=user_id)
            
            # Don't notify if user mentions themselves
            if mentioned_user.id == comment.user.id:
                print(f"⏭️ SIGNAL: Skipping self-mention for user {user_id}")
                continue
            
            print(f"🔔 SIGNAL: Creating mention notification for user {mentioned_user.id} ({mentioned_user.get_full_name()})")
            
            create_notification(
                user=mentioned_user,
                actor=comment.user,
                notification_type='post',
                title='You were mentioned',
                message=f"{comment.user.first_name} {comment.user.last_name} mentioned you in a comment",
                link_route='/alumni/home',
                link_params={'postId': comment.post.id},
                metadata={'comment_id': comment.id, 'mention_name': name}
            )
            
            notified_user_ids.add(user_id)
            print(f"✅ SIGNAL: Mention notification created successfully")
            
        except User.DoesNotExist:
            print(f"❌ SIGNAL: User {user_id} not found")
            continue
        except Exception as e:
            print(f"❌ SIGNAL: Error creating mention notification: {e}")
            import traceback
            traceback.print_exc()
            continue


# ========================================
# Reaction Notification Handlers
# ========================================

def notify_post_author_on_reaction(reaction, post):
    """
    Notify post author when someone reacts to their post.
    Skips if user is reacting to their own post.
    """
    if post.user != reaction.user:
        create_notification(
            user=post.user,
            actor=reaction.user,
            notification_type='post',
            title='New Reaction',
            message=f"{reaction.user.first_name} {reaction.user.last_name} reacted {reaction.emoji} to your post",
            link_route='/alumni/home',
            link_params={'postId': post.id},
            metadata={'reaction_type': reaction.reaction_type}
        )


def notify_comment_author_on_reaction(reaction, comment):
    """
    Notify comment author when someone reacts to their comment.
    Skips if user is reacting to their own comment.
    """
    if comment.user != reaction.user:
        create_notification(
            user=comment.user,
            actor=reaction.user,
            notification_type='post',
            title='New Reaction',
            message=f"{reaction.user.first_name} {reaction.user.last_name} reacted {reaction.emoji} to your comment",
            link_route='/alumni/home',
            link_params={'postId': comment.post.id},
            metadata={'reaction_type': reaction.reaction_type, 'comment_id': comment.id}
        )


# ========================================
# Signal Receivers
# ========================================

@receiver(post_save, sender=Comment)
def handle_comment_notifications(sender, instance, created, **kwargs):
    """
    Main signal handler for comment-related notifications.
    Triggers notifications for:
    - Post author (when someone comments on their post)
    - Parent comment author (when someone replies to their comment)
    - Mentioned users (when @mentioned in comment)
    """
    if not created:
        return
    
    # Check for mentions FIRST (works for all comments)
    detect_and_notify_mentions(instance)
    
    # Then notify based on comment type
    if instance.parent:
        # This is a reply to another comment
        notify_parent_comment_author_on_reply(instance)
    else:
        # This is a direct comment on a post
        notify_post_author_on_comment(instance)


@receiver(post_save, sender=Reaction)
def handle_reaction_notifications(sender, instance, created, **kwargs):
    """
    Main signal handler for reaction-related notifications.
    Triggers notifications for:
    - Post author (when someone reacts to their post)
    - Comment author (when someone reacts to their comment)
    """
    if not created:
        return
    
    content_type = instance.content_type
    
    # Handle reaction on Post
    if content_type.model == 'post':
        from .models import Post
        try:
            post = Post.objects.get(id=instance.object_id)
            notify_post_author_on_reaction(instance, post)
        except Post.DoesNotExist:
            pass
    
    # Handle reaction on Comment
    elif content_type.model == 'comment':
        try:
            comment = Comment.objects.get(id=instance.object_id)
            notify_comment_author_on_reaction(instance, comment)
        except Comment.DoesNotExist:
            pass

