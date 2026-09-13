from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'user_public'

urlpatterns = [
    path('teacher/<int:pk>', views.TeacherPublicDetailView.as_view(), name='teacher_detail'),
    path('teacher/list/', views.TeacherPublicListView.as_view(), name='teacher_list'),
    path('division/<int:pk>', views.DivisionPublicDetailView.as_view(), name='division_detail'),
    path('division/list/', views.DivisionPublicListView.as_view(), name='division_list'),
    path('review/dashboard/', views.ReviewDashboardView.as_view(), name='review_dashboard'),
    path('submissions/', views.TeacherSubmissionView.as_view(), name='teacher_submissions'),
    path('password/change/', views.ForcedPasswordChangeView.as_view(), name='password_change'),
    path('password/change/done/', views.ForcedPasswordChangeDoneView.as_view(), name='password_change_done'),
]
