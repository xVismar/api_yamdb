"""Модуль с маршрутизацией приложения api."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    CategoryViewSet, GenreViewSet, ReviewViewSet, TitleViewSet,
    CommentViewSet, UserViewSet, ObtainJWTView, SignUpView
)

app_name = 'api'

router_v1 = DefaultRouter()
router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register('titles', TitleViewSet, basename='titles')
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
router_v1.register('users', UserViewSet, basename='users')


auth_url_patterns = [
    path('signup/', SignUpView.as_view()),
    path('token/', ObtainJWTView.as_view()),
]

api_version_url_patterns = [
    path('', include(router_v1.urls)),
    path('auth/', include(auth_url_patterns)),
]

urlpatterns = [
    path('v1/', include(api_version_url_patterns)),
]
