from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, signup, token

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path('v1/', include(router.urls)),

    path('v1/auth/signup/', signup, name='signup'),
    path('v1/auth/token/', token, name='token'),
]
