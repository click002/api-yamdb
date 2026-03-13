import random

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from .permissions import IsAdminOrReadOnly, IsAuthorOrAdmin
from .serializers import UserCreateSerializer, UserSerializer

User = get_user_model()


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
        else:
            permission_classes = [IsAdminOrReadOnly]
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

        serializer = self.get_serializer(
            user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)

        if 'role' in serializer.validated_data and not (
            user.role == 'admin' or user.is_superuser
        ):
            serializer.validated_data.pop('role')

        serializer.save()
        return Response(serializer.data)
