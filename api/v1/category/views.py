from django.contrib.auth.models import Group
from rest_framework import generics
from category.models import Category, CoefficientCategoryByYear
from . import serializers


class CreateCategoryApiView(generics.CreateAPIView):
    queryset = Category.objects.all()
    model = Category
    serializer_class = serializers.CategorySerializer


class GetUpdateDeleteCategoryView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    model = Category
    serializer_class = serializers.CategorySerializer


class ReportCategoryView(generics.ListAPIView):
    queryset = Category.objects.exclude(id=29)  # TODO id 29 - стартовый бал фильтр
    serializer_class = serializers.CategoryReportSerializer


class ReportGroupyView(generics.ListAPIView):
    queryset = Group.objects.all()
    serializer_class = serializers.GroupSerializer


class CoefficientCategoryByYearCreateApiView(generics.CreateAPIView):
    queryset = CoefficientCategoryByYear.objects.all()
    model = CoefficientCategoryByYear
    serializer_class = serializers.CoefficientCategoryByYearSerializer


class CoefficientCategoryByYearCategoryRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CoefficientCategoryByYear.objects.all()
    model = CoefficientCategoryByYear
    serializer_class = serializers.CoefficientCategoryByYearSerializer
