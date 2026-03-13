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
]
