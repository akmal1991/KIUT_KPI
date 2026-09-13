"""Inspector-side scoping and decision logic for the review dashboard."""
from django.utils import timezone


def reviewer_visible_posts(user):
    from post.models import Post
    from user.models import User

    if not user.is_authenticated:
        return Post.objects.none()

    if user.is_superuser or user.role == User.Role.INSPECTOR:
        return Post.objects.all()

    return Post.objects.none()


def apply_decision(post, reviewer, action, comment=''):
    post.status = 2 if action == 'approve' else 3
    post.review_comment = comment or ''
    post.reviewed_by = reviewer
    post.reviewed_at = timezone.now()
    post.save(update_fields=['status', 'review_comment', 'reviewed_by', 'reviewed_at'])
    return post
