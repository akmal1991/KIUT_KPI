# Seeds the five KIUT RBAC roles as Django Groups with model-level permissions.
#
# Django's auth permissions are model-wide (not row-scoped), so "own submissions
# only" for FACULTY or "own kafedra only" for DEPARTMENT_REVIEWER are enforced in
# view/query code (see category.models.get_permission_queryset for the existing
# precedent), not by the group grant itself. This migration grants the closest
# correct model-level permission set for each role; ADMIN is intentionally not
# granted permissions here because ADMIN accounts are provisioned as Django
# superusers, which bypass the permission system entirely.
from django.db import migrations


ROLE_PERMISSIONS = {
    'FACULTY': [
        ('post', 'post', ['add_post', 'view_post']),
        ('post', 'document', ['add_document', 'view_document']),
    ],
    'DEPARTMENT_REVIEWER': [
        ('post', 'post', ['view_post', 'change_post']),
        ('post', 'document', ['view_document']),
        ('user', 'teacher', ['view_teacher']),
        ('user', 'division', ['view_division']),
    ],
    'SCIENTIFIC_DEPT_REVIEWER': [
        ('post', 'post', ['view_post', 'change_post', 'delete_post']),
        ('post', 'document', ['view_document', 'change_document']),
        ('post', 'academicyear', ['view_academicyear']),
        ('category', 'category', ['add_category', 'change_category', 'view_category']),
        ('category', 'categorytype', ['add_categorytype', 'change_categorytype', 'view_categorytype']),
        ('category', 'coefficientcategorybyyear', [
            'add_coefficientcategorybyyear', 'change_coefficientcategorybyyear', 'view_coefficientcategorybyyear',
        ]),
        ('category', 'statisticsscientific', ['view_statisticsscientific']),
        ('user', 'teacher', ['view_teacher']),
        ('user', 'division', ['view_division']),
    ],
    # SYSTEM is a service account for cron/automation (expiration sweeps, academic
    # year assignment, etc.) — it needs write access to the records those jobs
    # touch, but never logs in interactively, so it gets no admin-site-only perms.
    'SYSTEM': [
        ('post', 'post', ['add_post', 'change_post', 'view_post']),
        ('post', 'academicyear', ['add_academicyear', 'change_academicyear', 'view_academicyear']),
        ('category', 'category', ['view_category']),
    ],
}


def create_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    # ADMIN exists as a named role/group for reporting and future group-scoped
    # UI even though superuser accounts don't need its permissions to function.
    Group.objects.get_or_create(name='ADMIN')

    for role_name, grants in ROLE_PERMISSIONS.items():
        group, _ = Group.objects.get_or_create(name=role_name)
        codenames = []
        for app_label, model_name, perm_codenames in grants:
            try:
                ct = ContentType.objects.get(app_label=app_label, model=model_name)
            except ContentType.DoesNotExist:
                continue
            codenames.extend(
                Permission.objects.filter(content_type=ct, codename__in=perm_codenames)
            )
        group.permissions.set(codenames)


def remove_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(
        name__in=['FACULTY', 'DEPARTMENT_REVIEWER', 'SCIENTIFIC_DEPT_REVIEWER', 'ADMIN', 'SYSTEM']
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0008_user_role'),
        ('post', '0009_post_target'),
        ('category', '0008_coefficientcategorybyyear'),
        ('auth', '0012_alter_user_first_name_max_length'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.RunPython(create_groups, remove_groups),
    ]
