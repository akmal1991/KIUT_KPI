import datetime

from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Count, F, Sum, Q
from django.utils import timezone


class Division(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='division/images/', null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def get_total_teachers_count(self):
        return self.teacher_set.exclude(status=3).count()

    def get_total_ball(self):
        sum = 0
        for teacher in self.teacher_set.all():
            sum += teacher.get_total_ball()
        return round(sum, 1)

    def __str__(self):
        return self.name


class Target(models.Model):
    name = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"


class TeacherLevel(models.Model):
    name = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"


class AcademicLevel(models.Model):
    name = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"


class User(AbstractUser):
    class Role(models.TextChoices):
        FACULTY = 'FACULTY', 'Faculty'
        DEPARTMENT_REVIEWER = 'DEPARTMENT_REVIEWER', 'Department Reviewer'
        SCIENTIFIC_DEPT_REVIEWER = 'SCIENTIFIC_DEPT_REVIEWER', 'Scientific Department Reviewer'
        ADMIN = 'ADMIN', 'Administrator'
        SYSTEM = 'SYSTEM', 'System'

    class Status(models.TextChoices):
        PENDING_VERIFICATION = 'PENDING_VERIFICATION', 'Pending verification'
        ACTIVE = 'ACTIVE', 'Active'
        SUSPENDED = 'SUSPENDED', 'Suspended'

    father_name = models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField(upload_to='profile/images/', null=True, blank=True)
    birth = models.DateField(null=True, blank=True)
    division = models.ForeignKey(Division, null=True, blank=True, on_delete=models.CASCADE)
    phone = models.CharField(max_length=255, null=True, blank=True, unique=True)
    role = models.CharField(max_length=32, choices=Role.choices, default=Role.FACULTY)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.ACTIVE)
    email = models.EmailField(unique=True, blank=True)
    teacher_profile = models.OneToOneField(
        'Teacher', null=True, blank=True, on_delete=models.SET_NULL, related_name='user_account',
    )


class Teacher(models.Model):
    STATUS = ((1, 'Штатный'),
              (2, 'Совместитель'),
              (3, 'Выбыл'),
              (4, 'Почасовик'))

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    father_name = models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField(upload_to='profile/images/', null=True, blank=True)
    birth = models.DateField(null=True, blank=True)
    division = models.ForeignKey(Division, null=True, blank=True, on_delete=models.CASCADE)
    phone = models.CharField(max_length=255, null=True, blank=True)
    position = models.CharField(max_length=255, null=True, blank=True)
    level = models.ForeignKey(TeacherLevel, max_length=255, null=True, blank=True, on_delete=models.CASCADE)
    academic_title = models.ForeignKey(AcademicLevel, null=True, blank=True, on_delete=models.SET_NULL)
    uuid = models.CharField(max_length=255, null=True, blank=True)
    status = models.IntegerField(choices=STATUS, default=1)
    ext_date = models.DateField(null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def get_full_name(self):
        return "%s %s %s" % (self.last_name, self.first_name, self.father_name)

    def get_short_name(self):
        if not self.first_name:
            first_initial = ''
        else:
            first_initial = self.first_name[0]

        if self.father_name:
            if not self.father_name:
                father_initial = ''
            else:
                father_initial = self.father_name[0]
            return "%s %s. %s." % (self.last_name, first_initial, father_initial)

        return "%s %s." % (self.last_name, first_initial)

    def get_total_ball(self):
        sum_ball = 0
        for post in self.post_set.all():
            sum_ball += post.category.get_coef()
        return round(sum_ball, 1)

    def get_total_ball_by_year(self, academic_id):
        from post.models import AcademicYear
        academic_year = AcademicYear.objects.filter(id=academic_id).last()
        sum_bal = 0
        for post in self.post_set.filter(
                Q(academic_years=academic_year) | Q(category__id=29)).distinct():
            sum_bal += post.category.get_coef(academic_year=academic_year)
        return round(sum_bal, 1)

    def get_total_ball_by_group(self, group_id, academic_id):
        from post.models import AcademicYear
        academic_year = AcademicYear.objects.filter(id=academic_id).last()
        sum_bal = 0
        if group_id == 3:
            posts = self.post_set.filter(
                Q(category__group_id=group_id) & Q(academic_years=academic_year) | Q(category__id=29)
            ).distinct()
        else:
            posts = self.post_set.filter(Q(category__group_id=group_id) & Q(academic_years=academic_year)).distinct()

        for post in posts:
            sum_bal += post.category.get_coef(academic_year=academic_year)
        return round(sum_bal, 1)

    def get_limit_category(self, category, academic_year) -> bool:
        if not category.limit:
            return True
        posts = self.post_set.filter(academic_years=academic_year, category=category)
        if posts.count() > category.limit:
            return False
        return True

    @classmethod
    def teachers_exceeding_category_limits(cls, academic_year_id, category_id=None):
        from post.models import AcademicYear, Post
        from category.models import Category
        academic_year = AcademicYear.objects.get(id=academic_year_id)

        posts_in_year = Post.objects.filter(academic_years=academic_year, category__limit__isnull=False)
        if category_id:
            posts_in_year = posts_in_year.filter(category__id=category_id)

        teachers_posts = posts_in_year.values('teacher', 'category').annotate(total_posts=Count('id')).order_by()

        exceeding_teachers_ids = set()
        for item in teachers_posts:
            category_limit = Category.objects.get(id=item['category']).limit
            if item['total_posts'] > category_limit:
                exceeding_teachers_ids.add(item['teacher'])

        return Teacher.objects.filter(id__in=exceeding_teachers_ids)

    def __str__(self):
        return self.get_full_name()


class ControlLimit(models.Model):
    low_limit = models.IntegerField()
    high_limit = models.IntegerField()
    default_ball = models.ForeignKey('category.Category', on_delete=models.CASCADE)

    def __str__(self):
        return '%s - %s' % (self.low_limit, self.high_limit)


class EmailOTP(models.Model):
    """A one-time verification code for a User.email, used to activate a
    self-registered faculty account. The code is never stored in plaintext —
    only its Django password hash (PBKDF2-SHA256), the same hasher used for
    account passwords."""

    MAX_ATTEMPTS = 5
    VALIDITY_MINUTES = 10

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otp_codes')
    code_hash = models.CharField(max_length=255)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    attempts = models.PositiveSmallIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    @classmethod
    def issue(cls, user):
        """Generates a fresh 6-digit code for `user`, stores its hash, and
        returns the plaintext code (the only time it ever exists as plaintext)."""
        import secrets
        raw_code = f"{secrets.randbelow(1_000_000):06d}"
        otp = cls.objects.create(
            user=user,
            code_hash=make_password(raw_code),
            expires_at=timezone.now() + datetime.timedelta(minutes=cls.VALIDITY_MINUTES),
        )
        return otp, raw_code

    def is_expired(self):
        return timezone.now() >= self.expires_at

    def is_exhausted(self):
        return self.attempts >= self.MAX_ATTEMPTS

    def check_code(self, raw_code):
        """Verifies raw_code against the stored hash and records the attempt.
        Returns True only for a correct, unused, unexpired, non-exhausted code."""
        if self.is_used or self.is_expired() or self.is_exhausted():
            return False
        self.attempts += 1
        matched = check_password(raw_code, self.code_hash)
        if matched:
            self.is_used = True
        self.save(update_fields=['attempts', 'is_used'])
        return matched

    def __str__(self):
        return f"OTP for {self.user.email} (used={self.is_used}, expires={self.expires_at})"
