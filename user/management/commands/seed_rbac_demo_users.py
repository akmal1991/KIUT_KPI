from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.db import transaction

from user.models import User

# One demo login per RBAC role, for exercising role-gated behavior locally.
# Idempotent: safe to re-run against an existing database.
DEMO_ACCOUNTS = [
    {
        'username': 'faculty.demo',
        'email': 'faculty.demo@kiut.uz',
        'first_name': 'Faculty',
        'last_name': 'Demo',
        'role': User.Role.FACULTY,
        'password': 'Faculty@KIUT2024!',
        'is_staff': False,
        'is_superuser': False,
    },
    {
        'username': 'dept.reviewer',
        'email': 'dept.reviewer@kiut.uz',
        'first_name': 'Department',
        'last_name': 'Reviewer',
        'role': User.Role.DEPARTMENT_REVIEWER,
        'password': 'DeptReview@KIUT2024!',
        'is_staff': True,
        'is_superuser': False,
    },
    {
        'username': 'sci.reviewer',
        'email': 'sci.reviewer@kiut.uz',
        'first_name': 'Scientific Dept.',
        'last_name': 'Reviewer',
        'role': User.Role.SCIENTIFIC_DEPT_REVIEWER,
        'password': 'SciReview@KIUT2024!',
        'is_staff': True,
        'is_superuser': False,
    },
    {
        'username': 'system.bot',
        'email': 'system.bot@kiut.uz',
        'first_name': 'System',
        'last_name': 'Automation',
        'role': User.Role.SYSTEM,
        'password': None,  # service account: no interactive login, ever
        'is_staff': False,
        'is_superuser': False,
    },
]


class Command(BaseCommand):
    help = (
        "Seeds one demo user account per RBAC role (FACULTY, DEPARTMENT_REVIEWER, "
        "SCIENTIFIC_DEPT_REVIEWER, SYSTEM) and assigns the matching Django group. "
        "Also backfills role=ADMIN + ADMIN group membership onto existing superusers. "
        "Idempotent — safe to re-run."
    )

    @transaction.atomic
    def handle(self, *args, **options):
        for account in DEMO_ACCOUNTS:
            role = account['role']
            user, created = User.objects.get_or_create(
                username=account['username'],
                defaults={
                    'email': account['email'],
                    'first_name': account['first_name'],
                    'last_name': account['last_name'],
                    'role': role,
                    'is_staff': account['is_staff'],
                    'is_superuser': account['is_superuser'],
                    'is_active': True,
                },
            )
            if not created:
                user.role = role
                user.is_staff = account['is_staff']
                user.is_superuser = account['is_superuser']

            if account['password'] is None:
                user.set_unusable_password()
            else:
                user.set_password(account['password'])
            user.save()

            group, _ = Group.objects.get_or_create(name=role)
            user.groups.add(group)

            status = 'created' if created else 'updated'
            self.stdout.write(self.style.SUCCESS(f"[{status}] {user.username} -> role={role}"))

        admin_group, _ = Group.objects.get_or_create(name=User.Role.ADMIN)
        admins_updated = 0
        for admin_user in User.objects.filter(is_superuser=True):
            if admin_user.role != User.Role.ADMIN:
                admin_user.role = User.Role.ADMIN
                admin_user.save(update_fields=['role'])
            admin_user.groups.add(admin_group)
            admins_updated += 1
        self.stdout.write(self.style.SUCCESS(f"[synced] {admins_updated} existing superuser(s) -> role=ADMIN"))
