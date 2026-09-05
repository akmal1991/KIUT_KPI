from rest_framework.serializers import ModelSerializer, CurrentUserDefault
from user.models import Division
from rest_framework import serializers


class DivisionSerializer(ModelSerializer):
    class Meta:
        model = Division
        fields = ['id', 'name_uz', 'name_ru', 'name_en', 'image']
