from django.urls import path
from . import views

app_name = 'api_user'
urlpatterns = [
    path('teacher/create/', views.CreateTeacherApiView.as_view(), name='teacher_create'),
    path('teacher/<int:pk>', views.GetUpdateDeleteTeacherView.as_view(), name='teacher_get_update_delete'),
    path('teacher/list/', views.TeacherListApiView.as_view(), name='teacher_list'),
    path('teacher_level/create/', views.CreateTeacherLevelApiView.as_view(), name='teacher_level_create'),
    path('teacher_level/<int:pk>', views.GetUpdateDeleteTeacherLevelView.as_view(),
         name='teacher_level_get_update_delete'),
    path('teacher/<int:pk>/report/', views.TeacherYearReport.as_view(), name='teacher_report'),
    path('total/report/', views.AllYearReport.as_view(), name='total_report'),
    path('account/<int:pk>', views.GetUpdateUserAccountView.as_view(), name='account_update'),
]
