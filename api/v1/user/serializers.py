from rest_framework.serializers import ModelSerializer, CurrentUserDefault

from post.models import Post, AcademicYear
from user.models import Teacher, TeacherLevel, ControlLimit
from rest_framework import serializers


class TeacherSerializer(ModelSerializer):
    class Meta:
        model = Teacher
        fields = [
            'id', 'first_name_uz', 'first_name_ru', 'first_name_en', 'ext_date',
            'last_name_uz', 'last_name_ru', 'last_name_en',
            'father_name_uz', 'father_name_ru', 'father_name_en',
            'position_uz', 'position_ru', 'position_en', 'image', 'division',
            'level', 'status', 'uuid', 'academic_title'
        ]

    def create(self, validated_data):
        teacher = super(TeacherSerializer, self).create(validated_data)
        if ControlLimit.objects.last():
            Post.objects.create(teacher=teacher, title_ru='Стартовый балл', body_ru='Стартовый балл', status=2,
                                date=teacher.created, category=ControlLimit.objects.last().default_ball,
                                author=self.context['request'].user)
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
