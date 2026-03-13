from django.urls import path, include
from .views import ReviewViewSet, CommentViewSet
from rest_framework import routers

from .views import (
    CategoryViewSet,
    GenreViewSet,
    signup,
    TitleViewSet,
    token,
    UserViewSet,

)

# urlpatterns = [
#     path('titles/<int:title_id>/reviews/',
#          ReviewViewSet.as_view({
#              'get': 'list',
#              'post': 'create'
#          }),
#          name='review-list'),

#     path('titles/<int:title_id>/reviews/<int:pk>/',
#          ReviewViewSet.as_view({
#              'get': 'retrieve',
#              'put': 'update',
#              'patch': 'partial_update',
#              'delete': 'destroy'
#          }),
#          name='review-detail'),

#     path('titles/<int:title_id>/reviews/<int:review_id>/comments/',
#          CommentViewSet.as_view({
#              'get': 'list',
#              'post': 'create'
#          }),
#          name='comment-list'),

#     path('titles/<int:title_id>/reviews/<int:review_id>/comments/<int:pk>/',
#          CommentViewSet.as_view({
#              'get': 'retrieve',
#              'put': 'update',
#              'patch': 'partial_update',
#              'delete': 'destroy'
#          }),
#          name='comment-detail'),
# ]


router_v1 = routers.DefaultRouter()
router_v1.register('users', UserViewSet, basename='users')
router_v1.register('titles', TitleViewSet, basename='titles')
router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register('categories', CategoryViewSet, basename='сategories')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)


urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/auth/signup/', signup, name='signup'),
    path('v1/auth/token/', token, name='token'),
]
