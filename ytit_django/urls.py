"""ytit_django URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from django.contrib.auth.views import LoginView, LogoutView
from ytit_django import settings

# app_name = 'main'

urlpatterns = [
    path('login/', LoginView.as_view(template_name='administrator/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('api/', include('api.urls')),
    path('administrator/', include('ytit_django.urls_admin')),
    # Админка
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
handler404 = 'index.views.public_handler404'
urlpatterns += i18n_patterns(  # Публикации
    path('', include('index.urls_public')),  # Главная страница
    path('post/', include('post.urls_public')),  # Статьи
    path('category/', include('category.urls_public')),  # Категории
    path('user/', include('user.urls_public')),  # Пользователь
)
