from django.urls import path, include
from . import views

app_name = 'api_category'
urlpatterns = [
    path('create/', views.CreateCategoryApiView.as_view(), name='create'),
    path('<int:pk>', views.GetUpdateDeleteCategoryView.as_view(), name='get_update_delete'),
    path('report/', views.ReportCategoryView.as_view(), name='report'),
    path('report/group/', views.ReportGroupyView.as_view(), name='report_group'),

    path('create-coefficient/', views.CoefficientCategoryByYearCreateApiView.as_view(), name='create_coefficient'),
    path(
        '<int:pk>/update-coefficient/', views.CoefficientCategoryByYearCategoryRetrieveUpdateDestroyAPIView.as_view(),
        name='get_update_delete_coefficient'
    ),

]
