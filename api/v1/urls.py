from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path('category/', include('api.v1.category.urls')),
    path('division/', include('api.v1.division.urls')),
    path('user/', include('api.v1.user.urls')),
    path('post/', include('api.v1.post.urls')),
    path('review/', include('api.v1.review.urls')),

]