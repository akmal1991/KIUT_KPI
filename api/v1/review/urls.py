from django.urls import path

from . import views

app_name = 'api_review'
urlpatterns = [
    path('submissions/<int:pk>/decide/', views.SubmissionDecisionView.as_view(), name='decide'),
]
