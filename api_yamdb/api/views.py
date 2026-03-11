from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import mixins, viewsets, filters
from rest_framework.pagination import LimitOffsetPagination

from api.serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    TitleSerializer,
    UserSerializer,
)
from reviews.models import (
    Category,
    Comment,
    Genre,
    Review,
    Title,
    User
)


class User():
    pass


class GenreViewSet():
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class CategoryViewSet():
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class TitleViewSet(viewsets.ModelViewSet):
    serializer_class = TitleSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    search_fields = ['name']

    def get_queryset(self):
        return Title.objects.annotate(
            rating=Avg('reviews__score')
        ).order_by('name')
