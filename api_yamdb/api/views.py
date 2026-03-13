from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from reviews.models import Review, Comment
from reviews.models import Title
from .serializers import ReviewSerializer, CommentSerializer
from .permissions import IsAuthorOrModeratorOrAdmin


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet для отзывов."""
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrModeratorOrAdmin]

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        return title.reviews.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        serializer.save(author=self.request.user, title=title)
        self.update_title_rating(title_id)

    def perform_update(self, serializer):
        serializer.save()
        title_id = self.kwargs.get('title_id')
        self.update_title_rating(title_id)

    def perform_destroy(self, instance):
        title_id = instance.title.id
        instance.delete()
        self.update_title_rating(title_id)

    def update_title_rating(self, title_id):
        """Обновляет рейтинг произведения."""
        title = Title.objects.get(pk=title_id)
        average_score = title.reviews.aggregate(Avg('score'))['score__avg']
        title.rating = average_score or 0
        title.save(update_fields=['rating'])


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet для комментариев."""
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrModeratorOrAdmin]

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, pk=review_id)
        return review.comments.all()

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, pk=review_id)
        serializer.save(author=self.request.user, review=review)
