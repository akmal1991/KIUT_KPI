"""Shared helpers for provisioning a Teacher's login account, used by both
the Django admin (user.admin.TeacherAdmin) and the styled admin panel's
Add Teacher modal (api.v1.user.serializers.TeacherSerializer)."""
import secrets
import string


def generate_default_username():
    return 'teacher_' + secrets.token_hex(3)


def generate_default_password():
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(10))
