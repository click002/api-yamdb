import random

from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import (
    LimitOffsetPagination,
    PageNumberPagination
)
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import (
    Category,
    Genre,
    Review,
    Title,
    User
)
from api.serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    TitleReadSerializer,
    TitleWriteSerializer,
    UserSerializer
)
from .permissions import (
    IsAdminOrReadOnly,
    IsAuthorOrAdmin,
    IsAuthorOrModeratorOrAdmin,
    IsAdmin
)
from .filters import TitleFilter
from .serializers import UserCreateSerializer, UserSerializer


@api_view(['POST'])
@permission_classes([])
def signup(request):
    """Регистрация нового пользователя."""
    username = request.data.get('username')
    email = request.data.get('email')

    if not username or not email:
        errors = {}
        if not username:
            errors['username'] = ['Это поле обязательно.']
        if not email:
            errors['email'] = ['Это поле обязательно.']
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.filter(username=username, email=email).first()

    if user:
        confirmation_code = str(random.randint(10000, 99999))
        user.confirmation_code = confirmation_code
        user.save()

        send_mail(
            'Код подтверждения для YaMDb',
            f'Ваш новый код подтверждения: {confirmation_code}',
            'admin@yamdb.ru',
            [user.email],
            fail_silently=False,
        )

        return Response({
            'username': user.username,
            'email': user.email
        }, status=status.HTTP_200_OK)

    serializer = UserCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()

    confirmation_code = str(random.randint(10000, 99999))
    user.confirmation_code = confirmation_code
    user.save()

    send_mail(
        'Код подтверждения для YaMDb',
        f'Ваш код подтверждения: {confirmation_code}',
        'admin@yamdb.ru',
        [user.email],
        fail_silently=False,
    )

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([])
def token(request):
    """Получение JWT токена."""
    username = request.data.get('username')
    confirmation_code = request.data.get('confirmation_code')

    if not username or not confirmation_code:
        return Response(
            {'error': 'Необходимо указать username и confirmation_code'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = get_object_or_404(User, username=username)

    if user.confirmation_code != confirmation_code:
        return Response(
            {'error': 'Неверный код подтверждения'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user.confirmation_code = None
    user.save()

    token = AccessToken.for_user(user)
    return Response({'token': str(token)}, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    """Управление пользователями."""
    queryset = User.objects.all().order_by('username')
    serializer_class = UserSerializer
    lookup_field = 'username'
    pagination_class = PageNumberPagination
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    filter_backends = [filters.SearchFilter]
    search_fields = ['username']

    def get_permissions(self):
        """Права доступа для разных действий."""
        if self.action == 'me':
            permission_classes = [IsAuthorOrAdmin]
        elif self.action in [
            'list',
            'retrieve',
            'create',
            'update',
            'partial_update',
            'destroy']:
            permission_classes = [IsAdmin]
        else:
            permission_classes = [IsAdmin]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['get', 'patch', 'delete'], url_path='me')
    def me(self, request):
        """Свой профиль."""
        if not request.user.is_authenticated:
            return Response(
                {'detail': 'Authentication credentials were not provided.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if request.method == 'DELETE':
            return Response(
                {'detail': 'Method "DELETE" not allowed.'},
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )

        user = request.user

        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)

        # PATCH request
        serializer = self.get_serializer(
            user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)

        # Обычные пользователи не могут менять себе роль
        if 'role' in serializer.validated_data:
            if not (user.role == 'admin' or user.is_superuser):
                serializer.validated_data.pop('role')

        serializer.save()
        return Response(serializer.data)


# class UserViewSet(viewsets.ModelViewSet):
#     """Управление пользователями."""

#     queryset = User.objects.all().order_by('username')
#     serializer_class = UserSerializer
#     lookup_field = 'username'
#     pagination_class = PageNumberPagination
#     http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
#     filter_backends = [filters.SearchFilter]
#     search_fields = ['username']

#     def get_permissions(self):
#         """Права доступа для разных действий."""
#         if self.action == 'me':
#             permission_classes = [IsAuthorOrAdmin]
#         else:
#             permission_classes = [IsAdminOrReadOnly]
#         return [permission() for permission in permission_classes]

#     @action(detail=False, methods=['get', 'patch', 'delete'], url_path='me')
#     def me(self, request):
#         """Свой профиль."""
#         if not request.user.is_authenticated:
#             return Response(
#                 {'detail': 'Authentication credentials were not provided.'},
#                 status=status.HTTP_401_UNAUTHORIZED
#             )

#         if request.method == 'DELETE':
#             return Response(
#                 {'detail': 'Method "DELETE" not allowed.'},
#                 status=status.HTTP_405_METHOD_NOT_ALLOWED
#             )

#         user = request.user

#         if request.method == 'GET':
#             serializer = self.get_serializer(user)
#             return Response(serializer.data)

#         serializer = self.get_serializer(
#             user,
#             data=request.data,
#             partial=True
#         )
#         serializer.is_valid(raise_exception=True)

#         if 'role' in serializer.validated_data and not (
#             user.role == 'admin' or user.is_superuser
#         ):
#             serializer.validated_data.pop('role')

#         serializer.save()
#         return Response(serializer.data)


class CreateListDestroyViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    Базовый ViewSet:

    -создание
    -список
    -удаление.
    """
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = [IsAdminOrReadOnly]


class GenreViewSet(CreateListDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    lookup_field = 'slug'  # --------------


class CategoryViewSet(CreateListDestroyViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'  # --------------


class TitleViewSet(viewsets.ModelViewSet):
    http_method_names = [
        'get',
        'post',
        'patch',
        'delete',
        'head',
        'options'
    ]
    pagination_class = LimitOffsetPagination
    filter_backends = [
        DjangoFilterBackend,
    ]
    # filter_backends = [
    #     filters.SearchFilter,
    #     filters.OrderingFilter
    # ]
    filterset_class = TitleFilter
    permission_classes = [IsAdminOrReadOnly]

    # search_fields = ['name']

    def get_queryset(self):
        return Title.objects.annotate(
            rating=Avg('reviews__score')
        ).order_by('name')

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleWriteSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet для отзывов."""
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    serializer_class = ReviewSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        IsAuthorOrModeratorOrAdmin
    ]

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        return title.reviews.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        serializer.save(author=self.request.user, title=title)
        # self.update_title_rating(title_id)

    # def perform_update(self, serializer):
    #     serializer.save()
    #     title_id = self.kwargs.get('title_id')
    #     self.update_title_rating(title_id)

    # def perform_destroy(self, instance):
    #     title_id = instance.title.id
    #     instance.delete()
    #     self.update_title_rating(title_id)

    # def update_title_rating(self, title_id):
    #     """Обновляет рейтинг произведения."""
    #     title = Title.objects.get(pk=title_id)
    #     average_score = title.reviews.aggregate(Avg('score'))['score__avg']
    #     title.rating = average_score or 0
    #     title.save(update_fields=['rating'])


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet для комментариев."""
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    serializer_class = CommentSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        IsAuthorOrModeratorOrAdmin
    ]

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, pk=review_id)
        return review.comments.all()

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, pk=review_id)
        serializer.save(author=self.request.user, review=review)
