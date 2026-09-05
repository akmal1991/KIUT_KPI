from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from category.models import Category
from post.models import Post, PostCoAuthor
from user.models import Teacher

from . import doi_service
from .serializers import (
    CategoryPickerSerializer,
    CreateSubmissionSerializer,
    RespondCoAuthorRequestSerializer,
    SubmissionDetailSerializer,
    TeacherSearchResultSerializer,
)


class RequireTeacherProfileMixin:
    """Only a User with a linked Teacher profile can submit or review
    co-authorship requests — matches the faculty self-registration flow."""

    def get_lead_teacher(self, request):
        teacher = getattr(request.user, 'teacher_profile', None)
        if teacher is None:
            raise PermissionDenied('Your account has no linked teacher profile.')
        return teacher


class CategoryPickerView(generics.ListAPIView):
    """GET /api/v1/faculty/categories/ — feeds the Add Result modal's
    cascading Category -> Criterion picker, grouped by KPI domain."""

    permission_classes = [IsAuthenticated]
    serializer_class = CategoryPickerSerializer

    def get_queryset(self):
        return Category.objects.filter(self_submittable=True, is_delete=False).select_related('group')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        grouped = {}
        for category in queryset:
            group_name = category.group.name if category.group else 'Other'
            grouped.setdefault(group_name, []).append(self.get_serializer(category).data)
        return Response(grouped)


class DoiLookupView(APIView):
    """GET /api/v1/faculty/doi-lookup/?doi=... — proxies Crossref so the
    Add Result modal can auto-fill title/journal/ISSN/date/publisher."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        doi = request.GET.get('doi', '').strip()
        if not doi:
            return Response({'detail': 'doi query parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        result = doi_service.lookup_doi(doi)
        if result is None:
            return Response({'detail': 'DOI not found on Crossref.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(result)


class CreateSubmissionView(RequireTeacherProfileMixin, APIView):
    """POST /api/v1/faculty/submissions/ — creates a Post as the submitter's
    own Teacher (always lead author) plus pending PostCoAuthor rows for any
    tagged colleagues."""

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        lead_teacher = self.get_lead_teacher(request)
        serializer = CreateSubmissionSerializer(
            data=request.data, context={'request': request, 'lead_teacher': lead_teacher},
        )
        serializer.is_valid(raise_exception=True)
        post = serializer.save()
        return Response(SubmissionDetailSerializer(post).data, status=status.HTTP_201_CREATED)


class SubmissionDetailView(RequireTeacherProfileMixin, generics.RetrieveAPIView):
    """GET /api/v1/faculty/submissions/<id>/ — feeds the dashboard's
    slide-over drawer (evidence + review comment + co-author list)."""

    permission_classes = [IsAuthenticated]
    serializer_class = SubmissionDetailSerializer

    def get_queryset(self):
        teacher = self.get_lead_teacher(self.request)
        return Post.objects.filter(teacher=teacher)


class TeacherSearchView(RequireTeacherProfileMixin, generics.ListAPIView):
    """GET /api/v1/faculty/teacher-search/?q=... — the co-author tagger's
    search-as-you-type source. Excludes the current teacher (can't co-author
    yourself) and departed staff."""

    permission_classes = [IsAuthenticated]
    serializer_class = TeacherSearchResultSerializer

    def get_queryset(self):
        me = self.get_lead_teacher(self.request)
        query = self.request.GET.get('q', '').strip()
        queryset = Teacher.objects.exclude(status=3).exclude(id=me.id)
        if query:
            queryset = queryset.filter(Q(first_name__icontains=query) | Q(last_name__icontains=query))
        return queryset.order_by('last_name', 'first_name')[:10]


class RespondCoAuthorRequestView(RequireTeacherProfileMixin, APIView):
    """POST /api/v1/faculty/coauthor-requests/<id>/respond/ — the tagged
    colleague confirms or rejects being listed as a co-author."""

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        teacher = self.get_lead_teacher(request)
        co_author_request = get_object_or_404(PostCoAuthor, pk=pk, teacher=teacher, status=PostCoAuthor.Status.PENDING)

        serializer = RespondCoAuthorRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        co_author_request.status = (
            PostCoAuthor.Status.CONFIRMED if serializer.validated_data['action'] == 'confirm'
            else PostCoAuthor.Status.REJECTED
        )
        co_author_request.responded_at = timezone.now()
        co_author_request.save(update_fields=['status', 'responded_at'])

        return Response({'id': co_author_request.id, 'status': co_author_request.status})
