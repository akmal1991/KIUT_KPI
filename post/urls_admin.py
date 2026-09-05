from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'post_admin'

urlpatterns = [
    path('list/', views.PostListAdminView.as_view(), name='admin_list'),
    path('create/', views.PostCreateAdminView.as_view(), name='admin_create'),
    path('update/<int:pk>', views.PostUpdateAdminView.as_view(), name='admin_update'),

    path('reporting/', views.ReportingView.as_view(), name='admin_reporting'),
]
