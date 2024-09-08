"""Модуль с маршрутизацией приложения api."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet, GenreViewSet, ReviewViewSet, TitleViewSet,
    CommentViewSet, UserViewSet, obtain_jwt_view, sign_up_view,
    resend_confirmation_code_view
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
    path('signup/', sign_up_view),
    path('token/', obtain_jwt_view),
    path(
        'resend-confirmation-code/',
        resend_confirmation_code_view,
        name='resend_confirmation_code'
    ),

]


urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/auth/', include(auth_url_patterns)),
]
