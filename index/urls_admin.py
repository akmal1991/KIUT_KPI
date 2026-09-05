from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'index_admin'
urlpatterns = [
    path('', views.IndexAdminView.as_view(), name='index'),
]
