import datetime
from django.core.cache import cache
from django.contrib.auth.models import Group
from django.db.models import Count, F, Sum, Q
from user.models import User, Teacher
from django.db import models


def get_permission_queryset(user):
    if user.is_superuser:
        return Category.objects.all()
    return Category.objects.filter(group__in=user.groups.all())


class StatisticsScientific(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    category_types = models.ManyToManyField('CategoryType', null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def get_total_series(self):
        from post.models import AcademicYear

        cache_key = f'statistics_scientific_series_{self.id}_{self.updated}'
        cached_series = cache.get(cache_key)
        if cached_series:
            return cached_series

        series = []
        academic_years = list(AcademicYear.objects.all()[:5])
        for academic_year in reversed(academic_years):
            ball = 0
            for category_type in self.category_types.all():
                ball += category_type.get_total_ball_categories_date(academic_year)
            series.append(round(ball, 2))
        cache.set(cache_key, series, timeout=60 * 60)
        return series

    def __str__(self):
        return f"{self.name_ru} | {self.name_en} | {self.name_uz}"


class CategoryType(models.Model):
    name = models.CharField(max_length=255)
    categories = models.ManyToManyField('Category', null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def get_total_ball_categories_date(self, academic_year):
        ball = 0
        for category in self.categories.all():
            ball += category.get_total_ball_date(academic_year)
        return round(ball, 2)

    def get_total_series(self):
        cache_key = f'categorytype_{self.id}_total_series'
        cached_series = cache.get(cache_key)

        if cached_series:
            return cached_series

        series = []
        academic_years = list(AcademicYear.objects.all()[:5])
        for academic_year in reversed(academic_years):
            ball = 0
            for category in self.categories.all():
                ball += category.get_total_ball_date(academic_year)
            series.append(round(ball, 2))

        cache.set(cache_key, series, timeout=60 * 15)

        return series

    def __str__(self):
        return f"{self.name_ru} | {self.name_en} | {self.name_uz}"


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=255)
    is_delete = models.BooleanField(default=False)
    coef = models.FloatField()
    limit = models.IntegerField(null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name', 'group', 'coef']

    def get_coef(self, academic_year=None):
        if academic_year is None:
            from post.models import AcademicYear
            academic_year = AcademicYear.get_current_academic_year()

        cache_key = f"category_{self.id}_coef_{academic_year.id}"
        cached_coef = cache.get(cache_key)

        if cached_coef is not None:
            return cached_coef

        coefficient_category_by_year = self.coefficientcategorybyyear_set.filter(academic_year=academic_year)
        coef = coefficient_category_by_year.last().coef if coefficient_category_by_year else self.coef

        cache.set(cache_key, coef, timeout=60 * 60)  # Кэш на 1 час
        return coef

    def get_total_ball(self):
        return round(self.coef * self.post_set.filter(status=2).count(), 2)

    def get_total_ball_date(self, academic_year):
        return round(
            self.coef * self.post_set.filter(academic_years=academic_year, status=2).distinct().count(), 2,
        )

    @classmethod
    def get_categories_many_of_limit(cls, academic_year_id=None):
        from post.models import AcademicYear, Post

        if academic_year_id is None:
            academic_year = AcademicYear.get_current_academic_year()
        else:
            academic_year = AcademicYear.objects.get(id=academic_year_id)

        posts_counts = Post.objects.filter(academic_years=academic_year).values(
            'category', 'teacher'
        ).annotate(total_posts=Count('id')).order_by()

        category_ids = []
        for item in posts_counts:
            category = Category.objects.get(id=item['category'])
            if category.limit is not None and item['total_posts'] > category.limit:
                category_ids.append(category.id)

        return Category.objects.filter(id__in=category_ids).distinct()

    def __str__(self):
        return f"{self.id} | {self.name} | {self.coef}"


from post.models import AcademicYear


class CoefficientCategoryByYear(models.Model):
    class Meta:
        unique_together = ('category', 'academic_year')

    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.SET_NULL, null=True, blank=True)
    coef = models.FloatField()

    def __str__(self):
        return f"{self.category} | {self.academic_year} | {self.coef}"


class AcademicBall(models.Model):
    academic_year = models.OneToOneField(AcademicYear, null=True, blank=True, on_delete=models.CASCADE)
    gt_150 = models.IntegerField(null=True, blank=True, default=0)
    lt_150 = models.IntegerField(null=True, blank=True, default=0)
    lt_100 = models.IntegerField(null=True, blank=True, default=0)
    lt_55 = models.IntegerField(null=True, blank=True, default=0)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.academic_year} | {self.gt_150} | {self.lt_150} | {self.lt_100} | {self.lt_55}"
