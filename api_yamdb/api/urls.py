from django.urls import path
from .views import ReviewViewSet, CommentViewSet

urlpatterns = [
    path('titles/<int:title_id>/reviews/',
         ReviewViewSet.as_view({
             'get': 'list',
             'post': 'create'
         }),
         name='review-list'),

    path('titles/<int:title_id>/reviews/<int:pk>/',
         ReviewViewSet.as_view({
             'get': 'retrieve',
             'put': 'update',
             'patch': 'partial_update',
             'delete': 'destroy'
         }),
         name='review-detail'),

    path('titles/<int:title_id>/reviews/<int:review_id>/comments/',
         CommentViewSet.as_view({
             'get': 'list',
             'post': 'create'
         }),
         name='comment-list'),

    path('titles/<int:title_id>/reviews/<int:review_id>/comments/<int:pk>/',
         CommentViewSet.as_view({
             'get': 'retrieve',
             'put': 'update',
             'patch': 'partial_update',
             'delete': 'destroy'
         }),
         name='comment-detail'),
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
