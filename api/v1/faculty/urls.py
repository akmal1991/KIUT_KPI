from django.urls import path

from . import views

app_name = 'api_faculty'

urlpatterns = [
    path('categories/', views.CategoryPickerView.as_view(), name='categories'),
    path('doi-lookup/', views.DoiLookupView.as_view(), name='doi_lookup'),
    path('submissions/', views.CreateSubmissionView.as_view(), name='submission_create'),
    path('submissions/<int:pk>/', views.SubmissionDetailView.as_view(), name='submission_detail'),
    path('teacher-search/', views.TeacherSearchView.as_view(), name='teacher_search'),
    path(
        'coauthor-requests/<int:pk>/respond/',
        views.RespondCoAuthorRequestView.as_view(),
        name='coauthor_respond',
    ),
]
