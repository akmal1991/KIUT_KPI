from datetime import date

from django.contrib.auth.models import Group
from rest_framework.serializers import ModelSerializer, CurrentUserDefault
from category.models import Category, CoefficientCategoryByYear
from rest_framework import serializers

from post.models import AcademicYear


class CoefficientCategoryByYearSerializer(ModelSerializer):
    class Meta:
        model = CoefficientCategoryByYear
        fields = '__all__'


class CategorySerializer(ModelSerializer):
    author = serializers.HiddenField(default=CurrentUserDefault())

    class Meta:
        model = Category
        fields = ['id', 'author', 'name_uz', 'name_ru', 'name_en', 'coef', 'group', 'limit']


class CategoryReportSerializer(ModelSerializer):
    ball = serializers.FloatField(source='get_total_ball')

    class Meta:
        model = Category
        fields = ['id', 'name_uz', 'name_ru', 'name_en', 'ball']


class GroupSerializer(ModelSerializer):
    ball = serializers.SerializerMethodField(source='get_total_ball')
    minus_ball = serializers.SerializerMethodField()

    def get_minus_ball(self, obj):

        academic_year = AcademicYear.get_current_academic_year()

        total_ball = 0
        for category in obj.category_set.filter(coef__lt=0):
            total_ball -= category.get_total_ball_date(academic_year)

        return total_ball

    def get_ball(self, obj):

        academic_year = AcademicYear.get_current_academic_year()

        try:
            if self.context['request'].GET.get("academic_year"):
                academic_year_id = int(self.context['request'].GET.get("academic_year"))
                academic_year = AcademicYear.objects.get(id=academic_year_id)
        except:
            pass

        total_ball = 0
        for category in obj.category_set.filter(coef__gt=0):
            total_ball += category.get_total_ball_date(academic_year)
        return total_ball

    class Meta:
        model = Group
        fields = ['id', 'name', 'ball', 'minus_ball']
