from django.urls import path

from . import views

app_name = 'api_auth'

urlpatterns = [
    path('faculty/register/', views.FacultyRegisterView.as_view(), name='faculty_register'),
    path('faculty/verify-otp/', views.VerifyOtpView.as_view(), name='faculty_verify_otp'),
    path('faculty/resend-otp/', views.ResendOtpView.as_view(), name='faculty_resend_otp'),
]
