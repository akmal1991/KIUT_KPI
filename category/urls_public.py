from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'category_public'
urlpatterns = [
    path('list/', views.CategoryAdminListView.as_view(), name='list'),
    path('statistics/scientific/', views.StatisticsScientificView.as_view(), name='static'),
]
