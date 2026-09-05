from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'index_public'
urlpatterns = [
    path('', views.IndexPublicView.as_view(), name='index'),
]
