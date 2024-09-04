"""Модуль с маршрутизацией приложения api."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, GenreViewSet, ReviewViewSet, TitleViewSet

app_name = 'api'

router = DefaultRouter()

router.register('genres', GenreViewSet)
router.register('categories', CategoryViewSet)
router.register('titles', TitleViewSet)
router.register(r'titles/(?P<title_id>\d+)/?reviews/?',
                ReviewViewSet, basename='review')


api_version_patterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls.jwt'))
]

urlpatterns = [
    path('v1/', include(api_version_patterns)),
]
