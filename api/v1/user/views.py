from datetime import datetime, date, timedelta
from django.db.models import Prefetch
from django.contrib.auth.models import Group
from django.db.models import Sum, Q, FloatField, F, When, Case, IntegerField
from django.db.models.functions import Coalesce
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

import hashlib
from django.core.cache import cache

from post.models import Post, AcademicYear
from user.models import Teacher, TeacherLevel, Division, ControlLimit, User
from . import serializers
from ..post.paginatins import MyLimitOffsetPagination


class CreateTeacherApiView(generics.CreateAPIView):
    queryset = Teacher.objects.all()
    model = Teacher
    serializer_class = serializers.TeacherSerializer


class TeacherListApiView(generics.ListAPIView):
    queryset = Teacher.objects.exclude(status=3)
    model = Teacher
    serializer_class = serializers.TeacherStatisticSerializer
    pagination_class = MyLimitOffsetPagination

    def get_queryset(self):
        academic_id = self.request.GET.get('academic_year')
        cache_key = self.get_cache_key(academic_id)
        cached_teachers = cache.get(cache_key)

        if cached_teachers:
            return cached_teachers

        if academic_id:
            try:
                academic_year = AcademicYear.objects.filter(id=int(academic_id)).last()
            except:
                academic_year = AcademicYear.get_current_academic_year()
        else:
            academic_year = AcademicYear.get_current_academic_year()

        teachers = Teacher.objects.annotate(
            X_total_ball=Coalesce(
                Sum(
                    Case(
                        When(
                            post__category__coefficientcategorybyyear__academic_year=academic_year,
                            then=F('post__category__coefficientcategorybyyear__coef')
                        ),
                        default=F('post__category__coef'),
                        output_field=FloatField()
                    ),
                    filter=Q(post__academic_years=academic_year) | Q(post__category__id=29)
                ),
                0,
                output_field=FloatField()
            )
        ).order_by("-X_total_ball").exclude(status=3).distinct()

        cache.set(cache_key, teachers, timeout=60 * 60)
        return teachers

    def get_cache_key(self, academic_id):
        """Generate a unique cache key based on query parameters."""
        params = f'academic_year={academic_id}'
        return hashlib.md5(params.encode('utf-8')).hexdigest()


class GetUpdateDeleteTeacherView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Teacher.objects.all()
    model = Teacher
    serializer_class = serializers.TeacherSerializer


class CreateTeacherLevelApiView(generics.CreateAPIView):
    queryset = TeacherLevel.objects.all()
    model = TeacherLevel
    serializer_class = serializers.TeacherLevelSerializer


class GetUpdateDeleteTeacherLevelView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TeacherLevel.objects.all()
    model = TeacherLevel
    serializer_class = serializers.TeacherLevelSerializer


class TeacherYearReport(generics.RetrieveAPIView):
    queryset = Teacher.objects.all()
    model = Teacher

    def get(self, request, *args, **kwargs):

        teacher = self.get_object()
        response = {}
        response['academic_years'] = []
        response['group'] = []

        for group in Group.objects.all():
            response['group'].append({'name': group.name, 'category': [], 'total_balls': [], "id": group.id})

            total_balls = [0, 0, 0, 0, 0]
            for category in group.category_set.filter(post__teacher=teacher).distinct():
                balls = []
                academic_years = AcademicYear.objects.all()[:5]
                for academic_year in reversed(academic_years):
                    coefficient = category.get_coef(academic_year)
                    response['academic_years'].append(academic_year.years)
                    balls.append(
                        Post.objects.filter(category=category, teacher=teacher,
                                            academic_years=academic_year).count() * coefficient)

                if category.id == 29:  # Если стартовый балл, то должен для каждого года считать стартовый балл
                    balls = [max(balls)] * len(balls)
                total_balls = map(sum, zip(total_balls, balls))

                response['group'][-1]['category'].append({
                    "name": category.name,
                    "balls": balls,
                })

            response['group'][-1]['total_balls'] = total_balls

        if ControlLimit.objects.last():
            response['low_line'] = ControlLimit.objects.last().low_limit
            response['high_line'] = ControlLimit.objects.last().high_limit
        return Response(response, status=200)


class AllYearReport(APIView):

    def get(self, request, *args, **kwargs):

        posts = Post.objects.all()
        response = {}
        response['year'] = sorted(set(posts.values_list("date__year", flat=True)))
        response['academic_years'] = []
        response['group'] = []

        for group in Group.objects.all():
            response['group'].append({'name': group.name, 'category': [], 'total_balls': [], "id": group.id})

            total_balls = [0] * len(response['year'])
            for category in group.category_set.all():
                balls = []
                academic_years = AcademicYear.objects.all()[:5]
                for academic_year in reversed(academic_years):
                    coefficient = category.get_coef(academic_year)
                    response['academic_years'].append(academic_year.years)
                    balls.append(
                        Post.objects.filter(category=category, academic_years=academic_year).count() * coefficient)

                if category.id == 29:  # Если стартовый балл, то должен для каждого года считать стартовый балл
                    balls = [max(balls)] * len(balls)
                total_balls = map(sum, zip(total_balls, balls))

                response['group'][-1]['category'].append({
                    "name": category.name,
                    "balls": balls,
                })

            response['group'][-1]['total_balls'] = total_balls

        return Response(response, status=200)


class GetUpdateUserAccountView(generics.RetrieveUpdateAPIView):
    """Assigns a role (and division, for Department Reviewers) to an
    existing login account — see UserAccountAdminListView."""

    queryset = User.objects.all()
    serializer_class = serializers.UserAccountSerializer
