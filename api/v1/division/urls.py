from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from . import views

app_name = 'api_division'
urlpatterns = [
    # path('create/', views.CreateDivisionApiView.as_view(), name='create'),
    # path('<int:pk>', views.GetUpdateDeleteDivisionView.as_view(), name='get_update_delete'),
    path('<int:pk>/report/', views.DivisionYearReport.as_view(), name='report'),

]
