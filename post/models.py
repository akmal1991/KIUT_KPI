from django.forms import forms
from datetime import datetime, date, timedelta
from user.models import User
from django.db import models
from user.models import Teacher, Target
# Create your models here.
from category.models import Category
from django.db.models import ObjectDoesNotExist


class AcademicYear(models.Model):
    class Meta:
        ordering = ['-from_date']

    years = models.CharField(max_length=255, null=True, blank=True)
    from_date = models.DateField()
    to_date = models.DateField()

    def save(self, *args, **kwargs):
        self.years = f"{self.from_date.year}-{self.to_date.year}"
        super(AcademicYear, self).save(*args, **kwargs)

    def clean(self):
        if self.from_date >= self.to_date:
            raise forms.ValidationError(
                {'from_date': 'The to date field must be small', 'to_date': 'The from date field must be large'},
            )

    @classmethod
    def get_current_academic_year(cls):
        today = date.today()
        try:
            return cls.objects.get(from_date__lte=today, to_date__gte=today)
        except ObjectDoesNotExist:
            return None

    def __str__(self):
        return f"{self.id} | {self.years}"


class Post(models.Model):
    class Meta:
        ordering = ['-date', ]

    QUARTILE_CHOICES = (
        ('Q1', 'Q1'),
        ('Q2', 'Q2'),
        ('Q3', 'Q3'),
        ('Q4', 'Q4'),
    )

    STATUS_CHOICES = (
        (1, 'На рассмотрении'),
        (2, 'Одобрено'),
        (3, 'Отклонено'),
    )
    title = models.CharField(max_length=255)
    body = models.TextField()
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)
    indexing = models.CharField(max_length=255, null=True, blank=True)
    source = models.CharField(max_length=1255, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    target = models.ForeignKey(Target, on_delete=models.SET_NULL, null=True, blank=True)
    academic_years = models.ForeignKey(AcademicYear, null=True, blank=True, on_delete=models.SET_NULL)

    # Faculty self-submission workflow (DOI-backed research entries, review trail).
    doi = models.CharField(max_length=255, null=True, blank=True)
    quartile = models.CharField(max_length=2, choices=QUARTILE_CHOICES, null=True, blank=True)
    estimated_score = models.FloatField(
        null=True, blank=True,
        help_text="Computed at submission time from the category rule and the submitter's author share.",
    )
    validated_score = models.FloatField(
        null=True, blank=True, help_text="Set by the reviewer at approval time; may differ from the estimate.",
    )
    review_comment = models.TextField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name='reviewed_posts',
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.date:
            academic_year = AcademicYear.objects.filter(
                from_date__lte=self.date, to_date__gte=self.date).last()
        else:
            today = date.today()
            academic_year = AcademicYear.objects.filter(
                from_date__lte=today, to_date__gte=today).last()
        self.academic_years = academic_year
        super(Post, self).save(*args, **kwargs)

    def academic_year(self):
        if self.date.month < 9:
            return f'{self.date.year - 1} - {self.date.year}'
        return f'{self.date.year} - {self.date.year + 1}'

    def __str__(self):
        return "%s: %s (%s)" % (self.teacher.get_full_name(), self.title, self.category.name)


class PostCoAuthor(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        CONFIRMED = 'CONFIRMED', 'Confirmed'
        REJECTED = 'REJECTED', 'Rejected'

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='co_authors')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='co_author_requests')
    share_percent = models.FloatField()
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    requested_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('post', 'teacher')

    def __str__(self):
        return f"{self.teacher} on {self.post_id} ({self.status})"


class Document(models.Model):
    file = models.FileField(upload_to='post/document/')
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id} | {self.file}"
