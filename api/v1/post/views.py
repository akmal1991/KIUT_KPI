import datetime
from datetime import date, timedelta

from django.contrib.auth.models import Group
from django.db.models import Q, Sum
from django.http import FileResponse
from rest_framework import generics
from rest_framework.views import APIView

from django.core.cache import cache

from post.excel_sevice import excel_writer, excel_teachers, excel_teachers_form2
from post.models import Post, AcademicYear
from . import serializers
from rest_framework.response import Response
from category.models import get_permission_queryset
from .paginatins import MyLimitOffsetPagination


class CreatePostApiView(generics.CreateAPIView):
    queryset = Post.objects.all()
    model = Post
    serializer_class = serializers.PostSerializer


class GetUpdateDeletePostView(generics.RetrieveUpdateDestroyAPIView):
    model = Post
    serializer_class = serializers.PostSerializer

    def get_queryset(self):
        return Post.objects.filter(category__in=get_permission_queryset(self.request.user))


class PostListView(generics.ListAPIView):
    serializer_class = serializers.PostStatisticSerializer
    pagination_class = MyLimitOffsetPagination

    def get_queryset(self):
        posts = Post.objects.order_by("-id").exclude(author=4)
        return posts


class PostReportView(APIView):

    def get(self, request, *args, **kwargs):
        academic_id = self.request.GET.get('academic_year')
        if academic_id:
            try:
                academic_year = AcademicYear.objects.filter(id=int(academic_id)).last()
            except:
                academic_year = AcademicYear.get_current_academic_year()
        else:
            academic_year = AcademicYear.get_current_academic_year()

        groups = []
        for group in Group.objects.all():
            cache_key = f'group_{group.id}_year_{academic_year.id}'
            cache_key_minus = f'group_minus_{group.id}_year_{academic_year.id}'

            cached_group_data = cache.get(cache_key)
            # cached_group_data_minus = cache.get(cache_key_minus) if group.id == 3 else None

            # if cached_group_data:
            #     groups.append(cached_group_data)
            #     # if group.id == 3 and cached_group_data_minus:
            #     #     groups.append(cached_group_data_minus)
            #     continue

            from_date = academic_year.from_date
            to_date = academic_year.to_date

            total_ball_list = []
            # total_minus_ball_list = []

            while from_date < to_date:
                ball = 0
                # minus_ball = 0

                num_month = from_date.month
                if num_month == 12:
                    next_month = date(from_date.year + 1, 1, 1)
                else:
                    next_month = date(from_date.year, num_month + 1, 1)

                if next_month > to_date:
                    next_month = to_date + timedelta(days=1)

                if group.id == 3:  # id 3 - Академический
                    for post in Post.objects.filter(
                            (Q(date__gte=from_date, date__lt=next_month) & Q(category__group=group))
                            & ~Q(category_id=29), status=2).distinct():  # TODO id 29 - стартовый бал фильтр
                        # if post.category.get_coef(academic_year) > 0:
                        ball += post.category.get_coef(academic_year)
                        # else:
                        #     minus_ball -= post.category.get_coef(academic_year)
                else:
                    for post in Post.objects.filter(Q(date__gte=from_date, date__lt=next_month) & Q(
                            category__group=group), status=2):  # TODO id 29 - стартовый бал фильтр
                        ball += post.category.get_coef(academic_year)

                from_date = next_month

                # if num_month >= 9 and ball < 0:
                #     ball = 0
                total_ball_list.append(round(abs(ball), 1))
                # total_minus_ball_list.append(round(minus_ball, 1))

            group_data = {"group_name": group.name, "total_balls": total_ball_list, "id": group.id}

            cache.set(cache_key, group_data, timeout=60 * 60)
            groups.append(group_data)

            # if group.id == 3:
            #     minus_group_data = {"group_name": group.name, "total_balls": total_minus_ball_list, "id": -3}
            #     cache.set(f'group_minus_{group.id}_year_{academic_year.id}', minus_group_data, timeout=60 * 15)
            #     groups.append(minus_group_data)

        return Response(groups, status=200)


class PostsXlsx(APIView):

    def get(self, request, *args, **kwargs):
        academic_years = AcademicYear.objects.all().order_by('id')[3:]
        xlsx = excel_writer(academic_years)
        xlsx_file = open(f"{xlsx.filename}", 'rb')
        return FileResponse(xlsx_file)


class TeacherPostsXlsx(APIView):

    def get(self, request, *args, **kwargs):
        academic_id = self.request.GET.get('academic_year')
        division = self.request.GET.get('division')
        name = self.request.GET.get('name')
        uuid = self.request.GET.get('uuid')
        level = self.request.GET.get('level')
        order_by = self.request.GET.get('order_by')

        if academic_id:
            academic_year = AcademicYear.objects.filter(id=int(academic_id)).last()
        else:
            academic_year = AcademicYear.get_current_academic_year()

        xlsx = excel_teachers(
            academic_year=academic_year, division=division, name=name, uuid=uuid, level=level, order_by=order_by
        )
        xlsx_file = open(f"{xlsx.filename}", 'rb')
        return FileResponse(xlsx_file)


class TeacherPostsForm2Xlsx(APIView):

    def get(self, request, *args, **kwargs):
        academic_id = self.request.GET.get('academic_year')
        division = self.request.GET.get('division')
        name = self.request.GET.get('name')
        uuid = self.request.GET.get('uuid')
        level = self.request.GET.get('level')
        order_by = self.request.GET.get('order_by')

        if academic_id:
            academic_year = AcademicYear.objects.filter(id=int(academic_id)).last()
        else:
            academic_year = AcademicYear.get_current_academic_year()

        xlsx = excel_teachers_form2(
            academic_year=academic_year, division=division, name=name, uuid=uuid, level=level, order_by=order_by
        )
        xlsx_file = open(f"{xlsx.filename}", 'rb')
        return FileResponse(xlsx_file)


class UniquePostTitleAPIView(APIView):
    def get(self, request, *args, **kwargs):
        title_ru = request.GET.get('title_ru')
        title_en = "Weak gravitational lensing in sis plasma with gauss-bonnet theory"
        title_uz = "Weak gravitational lensing in sis plasma with gauss-bonnet theory"

        queries = []
        if title_ru:
            queries.append(Q(title=title_ru) | Q(title_ru=title_ru))
        if title_en:
            queries.append(Q(title=title_en) | Q(title_en=title_en))
        if title_uz:
            queries.append(Q(title=title_uz) | Q(title_uz=title_uz))

        if queries:
            query = queries.pop()
            for item in queries:
                query |= item
            post = Post.objects.filter(query).first()
            if post:
                return Response(status=200, data={"id": post.id})  # Используйте статус 200 для успешного ответа

        return Response(status=200, data={})
