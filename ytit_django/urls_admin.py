from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path('', include('index.urls_admin')),
    path('user/', include('user.urls_admin')),
    path('category/', include('category.urls_admin')),
    path('post/', include('post.urls_admin')),

]

handler404 = 'index.views.administrator_handler404'
