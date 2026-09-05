from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags
from rest_framework import serializers

from user.models import AcademicLevel, Division, EmailOTP, Teacher, TeacherLevel, User


def send_otp_email(user, raw_code):
    context = {
        'full_name': user.get_full_name() or user.first_name,
        'code': raw_code,
        'validity_minutes': EmailOTP.VALIDITY_MINUTES,
    }
    html_body = render_to_string('emails/faculty_otp.html', context)
    send_mail(
        subject='KIUT Portal — Email verification code',
        message=strip_tags(html_body),
        html_message=html_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )


class FacultyRegisterSerializer(serializers.Serializer):
    """Validates the registration form and creates a linked (User, Teacher)
    pair with User.status=PENDING_VERIFICATION. No password is collected —
    this system is passwordless: the OTP verification itself is the login."""

    image = serializers.ImageField(required=False, allow_null=True)
    full_name = serializers.CharField(max_length=255, trim_whitespace=True)
    division = serializers.PrimaryKeyRelatedField(queryset=Division.objects.all())
    position = serializers.CharField(max_length=255)
    academic_degree = serializers.PrimaryKeyRelatedField(
        queryset=AcademicLevel.objects.all(), required=False, allow_null=True,
    )
    academic_title = serializers.PrimaryKeyRelatedField(
        queryset=TeacherLevel.objects.all(), required=False, allow_null=True,
    )
    employment_type = serializers.ChoiceField(choices=Teacher.STATUS)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=255)

    def validate_email(self, value):
        value = value.strip().lower()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('An account with this email already exists.')
        return value

    def validate_phone(self, value):
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError('An account with this phone number already exists.')
        return value

    def _split_full_name(self, full_name):
        parts = full_name.split()
        if len(parts) == 1:
            return parts[0], ''
        return parts[0], ' '.join(parts[1:])

    def _unique_username(self, email):
        base = email.split('@')[0]
        username = base
        suffix = 1
        while User.objects.filter(username=username).exists():
            suffix += 1
            username = f"{base}{suffix}"
        return username

    def create(self, validated_data):
        first_name, last_name = self._split_full_name(validated_data['full_name'])

        teacher = Teacher.objects.create(
            first_name=first_name,
            last_name=last_name,
            image=validated_data.get('image'),
            division=validated_data['division'],
            position=validated_data['position'],
            academic_title=validated_data.get('academic_degree'),
            level=validated_data.get('academic_title'),
            status=validated_data['employment_type'],
            phone=validated_data['phone'],
        )

        user = User(
            username=self._unique_username(validated_data['email']),
            email=validated_data['email'],
            first_name=first_name,
            last_name=last_name,
            image=validated_data.get('image'),
            division=validated_data['division'],
            phone=validated_data['phone'],
            role=User.Role.FACULTY,
            status=User.Status.PENDING_VERIFICATION,
            teacher_profile=teacher,
        )
        user.set_unusable_password()
        user.save()

        otp, raw_code = EmailOTP.issue(user)
        send_otp_email(user, raw_code)

        return {'user': user, 'otp': otp}


class VerifyOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.RegexField(regex=r'^\d{6}$', error_messages={'invalid': 'The code must be exactly 6 digits.'})

    def validate(self, attrs):
        try:
            user = User.objects.get(email__iexact=attrs['email'], status=User.Status.PENDING_VERIFICATION)
        except User.DoesNotExist:
            raise serializers.ValidationError({'email': 'No pending registration found for this email.'})

        otp = user.otp_codes.filter(is_used=False).order_by('-created').first()
        if otp is None:
            raise serializers.ValidationError({'code': 'No active code was issued. Request a new one.'})
        if otp.is_expired():
            raise serializers.ValidationError({'code': 'This code has expired. Request a new one.'})
        if otp.is_exhausted():
            raise serializers.ValidationError({'code': 'Too many incorrect attempts. Request a new one.'})

        if not otp.check_code(attrs['code']):
            remaining = max(otp.MAX_ATTEMPTS - otp.attempts, 0)
            raise serializers.ValidationError({'code': f'Incorrect code. {remaining} attempt(s) remaining.'})

        attrs['user'] = user
        return attrs

    def save(self, **kwargs):
        user = self.validated_data['user']
        user.status = User.Status.ACTIVE
        user.save(update_fields=['status'])
        return user


class ResendOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email__iexact=value, status=User.Status.PENDING_VERIFICATION).exists():
            raise serializers.ValidationError('No pending registration found for this email.')
        return value

    def validate(self, attrs):
        user = User.objects.get(email__iexact=attrs['email'], status=User.Status.PENDING_VERIFICATION)
        last_otp = user.otp_codes.order_by('-created').first()
        if last_otp is not None:
            elapsed = (timezone.now() - last_otp.created).total_seconds()
            cooldown = settings.FACULTY_OTP_RESEND_COOLDOWN_SECONDS
            if elapsed < cooldown:
                raise serializers.ValidationError(
                    {'code': f'Please wait {int(cooldown - elapsed)}s before requesting another code.'}
                )
        attrs['user'] = user
        return attrs

    def save(self, **kwargs):
        user = self.validated_data['user']
        otp, raw_code = EmailOTP.issue(user)
        send_otp_email(user, raw_code)
        return otp
