"""Reviewer-side scoping and decision logic for the review dashboard.

DEPARTMENT_REVIEWER is scoped to their own division ("own kafedra only");
SCIENTIFIC_DEPT_REVIEWER (and superusers) see submissions university-wide.
"""
from django.utils import timezone


def reviewer_visible_posts(user):
    from post.models import Post
    from user.models import User

    if not user.is_authenticated:
        return Post.objects.none()

    if user.is_superuser or user.role == User.Role.SCIENTIFIC_DEPT_REVIEWER:
        return Post.objects.all()

    if user.role == User.Role.DEPARTMENT_REVIEWER:
        if not user.division_id:
            return Post.objects.none()
        return Post.objects.filter(teacher__division_id=user.division_id)

    return Post.objects.none()


def apply_decision(post, reviewer, action, comment=''):
    post.status = 2 if action == 'approve' else 3
    post.review_comment = comment or ''
    post.reviewed_by = reviewer
    post.reviewed_at = timezone.now()
    post.save(update_fields=['status', 'review_comment', 'reviewed_by', 'reviewed_at'])
    return post
