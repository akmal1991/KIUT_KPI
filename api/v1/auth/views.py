from django.contrib.auth import login
from django.urls import reverse
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from user.models import EmailOTP

from .serializers import FacultyRegisterSerializer, ResendOtpSerializer, VerifyOtpSerializer


def _issue_tokens(user):
    refresh = RefreshToken.for_user(user)
    refresh['email'] = user.email
    refresh['role'] = user.role
    access = refresh.access_token
    return {'access': str(access), 'refresh': str(refresh)}


class FacultyRegisterView(APIView):
    """POST /api/v1/auth/faculty/register/
    Multipart: image, full_name, division, position, academic_degree,
    academic_title, employment_type, email, phone.
    Creates the (User, Teacher) pair as PENDING_VERIFICATION and emails a
    6-digit OTP. Never returns the code."""

    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = FacultyRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        user = result['user']
        otp = result['otp']
        return Response(
            {
                'message': 'Registration received. Check your email for the verification code.',
                'email': user.email,
                'otp_expires_at': otp.expires_at,
                'otp_validity_minutes': EmailOTP.VALIDITY_MINUTES,
            },
            status=status.HTTP_201_CREATED,
        )


class VerifyOtpView(APIView):
    """POST /api/v1/auth/faculty/verify-otp/
    On success: activates the account, starts a Django session (so the
    browser can be redirected straight into the server-rendered dashboard),
    and also returns a JWT pair for any API/mobile client."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        tokens = _issue_tokens(user)

        return Response(
            {
                'message': 'Email verified. Your account is now active.',
                **tokens,
                'redirect_url': reverse('user_public:faculty_dashboard'),
            },
            status=status.HTTP_200_OK,
        )


class ResendOtpView(APIView):
    """POST /api/v1/auth/faculty/resend-otp/ — rate-limited to one request
    per FACULTY_OTP_RESEND_COOLDOWN_SECONDS."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResendOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp = serializer.save()
        return Response(
            {
                'message': 'A new verification code has been sent.',
                'otp_expires_at': otp.expires_at,
            },
            status=status.HTTP_200_OK,
        )
