from rest_framework import serializers

from category.models import Category
from post.models import Document, Post, PostCoAuthor
from post.scoring import estimate_score, max_total_authors
from user.models import Teacher


class CategoryPickerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'coef', 'distribution', 'max_co_authors',
            'co_author_share_percent', 'requires_doi', 'limit',
        ]


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'file']


class PostCoAuthorSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)

    class Meta:
        model = PostCoAuthor
        fields = ['id', 'teacher', 'teacher_name', 'share_percent', 'status']


class SubmissionDetailSerializer(serializers.ModelSerializer):
    documents = DocumentSerializer(many=True, read_only=True, source='document_set')
    co_authors = PostCoAuthorSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    reviewer_name = serializers.CharField(source='reviewed_by.get_full_name', read_only=True, default=None)

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'body', 'category', 'category_name', 'date', 'status',
            'doi', 'quartile', 'estimated_score', 'validated_score', 'review_comment',
            'reviewed_at', 'reviewer_name', 'documents', 'co_authors',
        ]


class CreateSubmissionSerializer(serializers.Serializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.filter(self_submittable=True))
    title = serializers.CharField(max_length=255)
    body = serializers.CharField(required=False, allow_blank=True, default='')
    date = serializers.DateField()
    doi = serializers.CharField(max_length=255, required=False, allow_blank=True)
    quartile = serializers.ChoiceField(choices=Post.QUARTILE_CHOICES, required=False, allow_blank=True)
    co_authors = serializers.PrimaryKeyRelatedField(
        queryset=Teacher.objects.all(), many=True, required=False, default=list,
    )
    files = serializers.ListField(
        child=serializers.FileField(), required=False, default=list, allow_empty=True,
    )

    def validate(self, attrs):
        category = attrs['category']
        lead_teacher = self.context['lead_teacher']

        if category.requires_doi and not attrs.get('doi'):
            raise serializers.ValidationError({'doi': 'This category requires a DOI.'})

        co_authors = attrs.get('co_authors') or []
        if lead_teacher in co_authors:
            raise serializers.ValidationError({'co_authors': "You can't tag yourself as a co-author."})

        capacity = max_total_authors(category)
        total_authors = 1 + len(co_authors)
        if total_authors > capacity:
            raise serializers.ValidationError({
                'co_authors': f'This category allows at most {capacity} total author(s); {total_authors} supplied.',
            })
        return attrs

    def create(self, validated_data):
        category = validated_data['category']
        lead_teacher = self.context['lead_teacher']
        author_user = self.context['request'].user
        title = validated_data['title']
        body = validated_data.get('body') or title

        # Written directly to every locale column: a submission's title/body
        # must be readable by a reviewer whose active language differs from
        # the submitter's — modeltranslation's plain `title=`/`body=` kwargs
        # only write the *current request's* active-language column.
        post = Post.objects.create(
            title=title, title_ru=title, title_en=title, title_uz=title,
            body=body, body_ru=body, body_en=body, body_uz=body,
            category=category,
            teacher=lead_teacher,
            author=author_user,
            date=validated_data['date'],
            doi=validated_data.get('doi') or None,
            quartile=validated_data.get('quartile') or None,
            status=1,
            estimated_score=estimate_score(category, is_lead=True),
        )

        for teacher in validated_data.get('co_authors') or []:
            PostCoAuthor.objects.create(
                post=post,
                teacher=teacher,
                share_percent=(
                    category.co_author_share_percent
                    if category.distribution == Category.Distribution.WEIGHTED_SPLIT else 100.0
                ),
            )

        for uploaded_file in validated_data.get('files') or []:
            Document.objects.create(post=post, file=uploaded_file, author=author_user)

        return post


class RespondCoAuthorRequestSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['confirm', 'reject'])


class TeacherSearchResultSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    division_name = serializers.CharField(source='division.name', read_only=True, default=None)

    class Meta:
        model = Teacher
        fields = ['id', 'full_name', 'division_name']
