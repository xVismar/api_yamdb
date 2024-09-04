"""Модуль с маршрутизацией приложения api."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, GenreViewSet, ReviewViewSet, TitleViewSet
from users.views import UserViewSet, ObtainJWTView, user_signup_view

app_name = 'api'

router = DefaultRouter()

router.register('genres', GenreViewSet)
router.register('categories', CategoryViewSet)
router.register('titles', TitleViewSet)
router.register(r'titles/(?P<title_id>\d+)/?reviews/?',
                ReviewViewSet, basename='review')
router.register(r'users', UserViewSet, basename='users')

api_version_patterns = [
    path('', include(router.urls)),
]

urlpatterns = [
    path('v1/auth/token/', ObtainJWTView.as_view(), name='token'),
    path('v1/auth/signup/', user_signup_view, name='signup'),
    path('v1/', include(api_version_patterns)),
]
