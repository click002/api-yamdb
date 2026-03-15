import random

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import (
    LimitOffsetPagination,
    PageNumberPagination
)
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from reviews.models import Category, Comment, Genre, Review, Title

from .permissions import (
    AllowAnyForSignup,
    IsAdmin,
    IsAdminOrModeratorOrReadOnly,
    IsAdminOrReadOnly,
    IsAdminUserOrReadOnlyForList,
    IsAuthorOrAdmin
)
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    TitleReadSerializer,
    TitleWriteSerializer,
    TokenSerializer,
    UserCreateSerializer,
    UserSerializer
)


User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAnyForSignup])
def signup(request):
    """Регистрация нового пользователя."""
    username = request.data.get('username')
    email = request.data.get('email')

    # Проверка наличия обязательных полей
    if not username or not email:
        errors = {}
        if not username:
            errors['username'] = ['Это поле обязательно.']
        if not email:
            errors['email'] = ['Это поле обязательно.']
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    # Проверяем, существует ли пользователь с такими username и email
    user = User.objects.filter(username=username, email=email).first()

    if user:
        # Пользователь уже существует – отправляем код подтверждения
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
        return Response(
            {'username': username, 'email': email},
            status=status.HTTP_200_OK
        )

    # Пользователь не найден – проверяем данные через сериализатор
    serializer = UserCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Дополнительная проверка уникальности полей (на случай, если кто-то пытается занять занятые)
    if User.objects.filter(username=username).exists():
        return Response(
            {'username': ['Пользователь с таким именем уже существует.']},
            status=status.HTTP_400_BAD_REQUEST
        )
    if User.objects.filter(email=email).exists():
        return Response(
            {'email': ['Пользователь с таким email уже существует.']},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Создаём нового пользователя
    user = User.objects.create_user(
        username=username,
        email=email
    )
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

    return Response(
        {'username': username, 'email': email},
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([AllowAnyForSignup])
def token(request):
    """Получение JWT токена."""
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    username = serializer.validated_data.get('username')
    confirmation_code = serializer.validated_data.get('confirmation_code')

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
        elif self.action in ['create', 'destroy', 'update', 'partial_update']:
            permission_classes = [IsAdmin]
        else:
            permission_classes = [IsAdminUserOrReadOnlyForList]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['get', 'patch'], url_path='me')
    def me(self, request):
        """Свой профиль."""
        user = request.user

        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)

        serializer = self.get_serializer(
            user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)

        if 'role' in serializer.validated_data:
            serializer.validated_data.pop('role')

        serializer.save()
        return Response(serializer.data)


class CreateListDestroyViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Базовый ViewSet: создание, список, удаление."""
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = [IsAdminOrReadOnly]


class GenreViewSet(CreateListDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    lookup_field = 'slug'


class CategoryViewSet(CreateListDestroyViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    pagination_class = LimitOffsetPagination
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.OrderingFilter]
    search_fields = ['name']

    def get_queryset(self):
        queryset = Title.objects.annotate(
            rating=Avg('reviews__score')
        ).order_by('name')

        # Фильтрация по genre
        genre_slug = self.request.query_params.get('genre')
        if genre_slug:
            queryset = queryset.filter(genre__slug=genre_slug)

        # Фильтрация по category
        category_slug = self.request.query_params.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        # Фильтрация по year
        year = self.request.query_params.get('year')
        if year:
            queryset = queryset.filter(year=year)

        # Фильтрация по name (точное совпадение)
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name=name)

        return queryset

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleWriteSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet для отзывов."""
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    serializer_class = ReviewSerializer
    permission_classes = [IsAdminOrModeratorOrReadOnly]

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet для комментариев."""
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    serializer_class = CommentSerializer
    permission_classes = [IsAdminOrModeratorOrReadOnly]

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
            title_id=self.kwargs.get('title_id')
        )
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
            title_id=self.kwargs.get('title_id')
        )
        serializer.save(author=self.request.user, review=review)
