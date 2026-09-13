from django.contrib.auth.hashers import make_password
from rest_framework.serializers import ModelSerializer, CurrentUserDefault

from post.models import Post, AcademicYear
from user.credentials import generate_default_password
from user.models import Teacher, TeacherLevel, ControlLimit, User
from rest_framework import serializers


class TeacherSerializer(ModelSerializer):
    # Optional login credentials, provisioned alongside the Teacher profile
    # from the Add Teacher modal — see user.admin.TeacherAdmin for the same
    # flow in Django's built-in admin.
    username = serializers.CharField(write_only=True, required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = Teacher
        fields = [
            'id', 'first_name_uz', 'first_name_ru', 'first_name_en', 'ext_date',
            'last_name_uz', 'last_name_ru', 'last_name_en',
            'father_name_uz', 'father_name_ru', 'father_name_en',
            'position_uz', 'position_ru', 'position_en', 'image', 'division',
            'level', 'status', 'uuid', 'academic_title', 'username', 'password',
        ]

    def validate_username(self, username):
        if username and User.objects.filter(username=username).exists():
            raise serializers.ValidationError('This username is already taken.')
        return username

    def create(self, validated_data):
        username = validated_data.pop('username', None)
        password = validated_data.pop('password', None)

        teacher = super(TeacherSerializer, self).create(validated_data)
        if ControlLimit.objects.last():
            Post.objects.create(teacher=teacher, title_ru='Стартовый балл', body_ru='Стартовый балл', status=2,
                                date=teacher.created, category=ControlLimit.objects.last().default_ball,
                                author=self.context['request'].user)

        if username:
            User.objects.create(
                username=username,
                # A leftover unique constraint on email predates this feature (from a
                # reverted migration never rolled back); a synthetic per-account
                # address avoids colliding with it without touching that schema.
                email=f'{username}@kiut.local',
                password=make_password(password or generate_default_password()),
                role=User.Role.FACULTY,
                teacher_profile=teacher,
                must_change_password=True,
            )
        return teacher


class TeacherStatisticSerializer(ModelSerializer):
    total_ball = serializers.SerializerMethodField(read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    def get_total_ball(self, obj):
        academic_id = self.context.get('request').GET.get('academic_year', None)
        if not academic_id:
            academic_id = AcademicYear.get_current_academic_year().id

        return obj.get_total_ball_by_year(academic_id)

    class Meta:
        model = Teacher
        fields = ['id', 'total_ball', 'position', 'full_name', 'first_name_uz', 'first_name_ru', 'first_name_en',
                  'last_name_uz', 'last_name_ru', 'last_name_en',
                  'father_name_uz', 'father_name_ru', 'father_name_en',
                  'position_uz', 'position_ru', 'position_en', 'image', 'division', 'level', 'status', 'uuid']

    def create(self, validated_data):
        teacher = super(TeacherStatisticSerializer, self).create(validated_data)
        if ControlLimit.objects.last():
            Post.objects.create(teacher=teacher, title_ru='Стартовый балл', body_ru='Стартовый балл', status=2,
                                date=teacher.created, category=ControlLimit.objects.last().default_ball,
                                author=self.context['request'].user)
        return teacher


class TeacherLevelSerializer(ModelSerializer):
    class Meta:
        model = TeacherLevel
        fields = ['id', 'name_uz', 'name_ru', 'name_en']
