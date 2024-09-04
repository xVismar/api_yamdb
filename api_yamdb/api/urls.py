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
router.register(r'titles/(?P<title_id>\d+)/?reviews/?(?P<review_id>\d+)/?',
                ReviewViewSet, basename='review')

router.register(r'users', UserViewSet, basename='users')

api_version_patterns = [
    path('', include(router.urls)),
    path('auth/signup/', user_signup_view, name='signup'),
    path('auth/token/', ObtainJWTView.as_view(), name='token')
]

urlpatterns = [
    path('v1/', include(api_version_patterns)),
]
