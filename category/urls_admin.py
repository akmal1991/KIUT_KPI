from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'category_admin'
urlpatterns = [
    path('list/', views.CategoryAdminListView.as_view(), name='list'),
    path('<int:pk>/coefficient-year/', views.CoefficientCategoryByYearAdminListView.as_view(), name='coefficient-year'),
]
