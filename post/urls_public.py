from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'post_public'

urlpatterns = [
    path('list/', views.PostListPublicView.as_view(), name='list'),
    path('<int:pk>', views.PostDetailPublicView.as_view(), name='detail'),
]
