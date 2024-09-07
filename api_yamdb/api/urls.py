"""Модуль с маршрутизацией приложения api."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    CategoryViewSet, GenreViewSet, ReviewViewSet, TitleViewSet, CommentViewSet, UserViewSet, ObtainJWTView, user_signup_view

)

app_name = 'api'
router_v1 = DefaultRouter()
router_v1.register('genres', GenreViewSet)
router_v1.register('categories', CategoryViewSet)
router_v1.register(
    r'titles',
    TitleViewSet,
    basename='titles'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comment'
)
router_v1.register(
    r'users',
    UserViewSet,
    basename='users'
)

auth_patterns = [
    path('signup/', user_signup_view, name='signup'),
    path('token/', ObtainJWTView.as_view(), name='token'),
]

api_version_patterns = [
    path('', include(router_v1.urls)),
    path('auth/', include(auth_patterns))
]


urlpatterns = [
    path('v1/', include(api_version_patterns)),
]
