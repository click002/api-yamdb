from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, signup, token

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path('v1/', include(router.urls)),

    path('v1/auth/signup/', signup, name='signup'),
    path('v1/auth/token/', token, name='token'),
from rest_framework import routers

from .views import (
    CategoryViewSet,
    GenreViewSet,
    TitleViewSet
)


router_v1 = routers.DefaultRouter()
router_v1.register('titles', TitleViewSet, basename='titles')
router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register('categories', CategoryViewSet, basename='сategories')


urlpatterns = [
    path('v1/', include(router_v1.urls)),
]
