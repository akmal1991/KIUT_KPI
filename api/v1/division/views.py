from datetime import date

from django.contrib.auth.models import Group
from rest_framework import generics
from rest_framework.response import Response

from category.models import Category
from post.models import Post, AcademicYear
from user.models import Division, ControlLimit
from . import serializers


class CreateDivisionApiView(generics.CreateAPIView):
    queryset = Division.objects.all()
    model = Division
    serializer_class = serializers.DivisionSerializer


class GetUpdateDeleteDivisionView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Division.objects.all()
    model = Division
    serializer_class = serializers.DivisionSerializer


class DivisionYearReport(generics.RetrieveAPIView):
    queryset = Division.objects.all()
    model = Division

    def get(self, request, *args, **kwargs):
        division = self.get_object()
        response = {}
        response['year'] = sorted(
            set(Post.objects.filter(teacher__division=division).distinct().values_list("academic_years__years",
                                                                                       flat=True)))
        response['group'] = []
        if len(response['year']) == 0:
            response['year'] = [AcademicYear.get_current_academic_year().years]

        for group in Group.objects.all():
            response['group'].append({'name': group.name, 'category': [], 'total_balls': [], 'id': group.id})
            total_balls = [0] * len(response['year'])
            for category in group.category_set.filter(post__teacher__division=division).distinct():
                balls = []
                for year in response['year']:
                    academic_year = AcademicYear.objects.get(years=year)
                    coefficient = category.get_coef(academic_year)

                    balls.append(
                        Post.objects.filter(
                            category=category,
                            teacher__division=division,
                            academic_years=academic_year
                        ).distinct().count() * coefficient)

                total_balls = map(sum, zip(total_balls, balls))
                response['group'][-1]['category'].append({"name": category.name, "balls": balls})

            response['group'][-1]['total_balls'] = total_balls

        if ControlLimit.objects.last():
            response['low_line'] = ControlLimit.objects.last().low_limit
            response['high_line'] = ControlLimit.objects.last().high_limit

        return Response(response, status=200)
