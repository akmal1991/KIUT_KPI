from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from . import views

app_name = 'api_post'
urlpatterns = [
    path('create/', views.CreatePostApiView.as_view(), name='create'),
    path('<int:pk>', views.GetUpdateDeletePostView.as_view(), name='get_update_delete'),
    path('list/', views.PostListView.as_view(), name='list'),
    path('report/', views.PostReportView.as_view(), name='report'),
    # xlsx
    path('xlsx/', views.PostsXlsx.as_view(), name='post_download_xlsx'),
    path('xlsx/teacher/', views.TeacherPostsXlsx.as_view(), name='teacher_download_xlsx'),
    path('xlsx/teacher-form2/', views.TeacherPostsForm2Xlsx.as_view(), name='teacher_form2_download_xlsx'),
    # unique post title
    path('unique/post-title/', views.UniquePostTitleAPIView.as_view(), name='unique_post_title')
]
