import bleach
from bleach.css_sanitizer import CSSSanitizer
from rest_framework.serializers import ModelSerializer, CurrentUserDefault
from user.models import Division
from rest_framework import serializers
from post.models import Post, AcademicYear
from category.models import get_permission_queryset, Category
from datetime import date

ALLOWED_BODY_TAGS = [
    'p', 'br', 'hr', 'span', 'strong', 'b', 'em', 'i', 'u',
    'ul', 'ol', 'li', 'h1', 'h2', 'h3', 'h4', 'a', 'img',
]
ALLOWED_BODY_ATTRIBUTES = {
    '*': ['style'],
    'a': ['href', 'title', 'target'],
    'img': ['src', 'alt'],
}
ALLOWED_BODY_PROTOCOLS = ['http', 'https', 'mailto']
BODY_CSS_SANITIZER = CSSSanitizer(allowed_css_properties=['text-align', 'font-size'])


class PostSerializer(ModelSerializer):
    author = serializers.HiddenField(default=CurrentUserDefault())

    def validate(self, data):
        """
        Check that the start is before the stop.
        """
        if not data['category'] in get_permission_queryset(self.context['request'].user):
            raise serializers.ValidationError("access denaid")
        for field in ('body_uz', 'body_ru', 'body_en'):
            if field in data and data[field]:
                data[field] = bleach.clean(
                    data[field],
                    tags=ALLOWED_BODY_TAGS,
                    attributes=ALLOWED_BODY_ATTRIBUTES,
                    protocols=ALLOWED_BODY_PROTOCOLS,
                    css_sanitizer=BODY_CSS_SANITIZER,
                    strip=True,
                )
        return data

    # def create(self, validated_data):
    #     post_category = validated_data.get('category')
    #     post_teacher = validated_data.get('teacher')
    #     data = validated_data.get('date')
    #     if not data:
    #         data = date.today()
    #     academic_year = AcademicYear.objects.filter(
    #         from_date__lte=data, to_date__gte=data).last()
    #     count_post = Post.objects.filter(teacher=post_teacher, category=post_category,
    #                                      academic_years=academic_year).count()
    #     if post_category.limit and count_post >= post_category.limit:
    #         raise serializers.ValidationError(f"У этого учителя {count_post} постов в этой категории.")
    #     return super(PostSerializer, self).create(validated_data)

    class Meta:
        model = Post
        fields = [
            'id', 'title_uz', 'title_ru', 'title_en', 'body_uz', 'body_ru', 'body_en',
            'category', 'teacher', 'author', 'date', 'indexing', 'status', 'source',
            'academic_years', 'target'
        ]


class PostStatisticSerializer(ModelSerializer):
    author = serializers.HiddenField(default=CurrentUserDefault())
    category_name = serializers.CharField(source='category.name', read_only=True)
    year = serializers.SerializerMethodField(read_only=True)

    def get_year(self, obj):
        if 9 <= obj.date.month <= 12:
            return f"{obj.date.year}-{obj.date.year + 1}"
        return f"{obj.date.year - 1}-{obj.date.year}"

    def validate(self, data):
        """
        Check that the start is before the stop.
        """
        if not data['category'] in get_permission_queryset(self.context['request'].user):
            raise serializers.ValidationError("access denaid")
        return data

    class Meta:
        model = Post
        fields = [
            'id', 'title_uz', 'title_ru', 'title_en', 'title',
            'category_name', 'year', 'body_uz', 'body_ru', 'body_en',
            'category', 'teacher', 'author', 'date', 'indexing', 'status'
        ]
