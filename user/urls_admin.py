from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'user_admin'
urlpatterns = [
    path('division/list/', views.DivisionAdminListView.as_view(), name='division_list'),
    path('teacher/list/', views.TeacherAdminListView.as_view(), name='teacher_list'),
    path('teacher/<int:pk>/', views.TeacherAdminDetailView.as_view(), name='teacher_detail'),
    path('teacher_level/list/', views.TeacherLevelAdminListView.as_view(), name='teacher_level_list'),
    path('account/list/', views.UserAccountAdminListView.as_view(), name='account_list'),

]
