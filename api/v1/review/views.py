from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from post.review import apply_decision, reviewer_visible_posts

from .serializers import ReviewDecisionSerializer


class SubmissionDecisionView(APIView):
    """POST /api/v1/review/submissions/<id>/decide/ — an Inspector approves
    or rejects a pending submission. Scoping the lookup itself (rather than
    fetching any Post and checking permission after) means an out-of-scope
    id 404s instead of 403ing, so it doesn't reveal that the id exists."""

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        post = get_object_or_404(reviewer_visible_posts(request.user), pk=pk)

        serializer = ReviewDecisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        apply_decision(post, request.user, data['action'], comment=data.get('comment', ''))
        return Response({'id': post.id, 'status': post.status}, status=status.HTTP_200_OK)
