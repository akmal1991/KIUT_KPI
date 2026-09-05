from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'user_public'

urlpatterns = [
    path('teacher/<int:pk>', views.TeacherPublicDetailView.as_view(), name='teacher_detail'),
    path('teacher/list/', views.TeacherPublicListView.as_view(), name='teacher_list'),
    path('division/<int:pk>', views.DivisionPublicDetailView.as_view(), name='division_detail'),
    path('division/list/', views.DivisionPublicListView.as_view(), name='division_list'),
]
