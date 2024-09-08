from datetime import timedelta
from random import sample

from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import (
    action, api_view, permission_classes, throttle_classes
)
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework_simplejwt.tokens import AccessToken

from api.filters import TitleFilter
from api.permissions import (
    AdminOnly, IsAuthorOrModeratorOrReadOnly, ReadOnlyOrAdmin
)
from api.serializers import (
    CategorySerializer, CommentSerializer, GenreSerializer,
    ObtainJWTSerializer, ReviewSerializer, SignUpSerializer,
    TitleReadSerializer, TitleWriteSerializer, UserProfileSerializer,
    UserSerializer
)
from reviews.models import Category, Genre, Review, Title, User


class BaseCRDSlugSeachViewset(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin
):
    permission_classes = (ReadOnlyOrAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    http_method_names = ['get', 'post', 'patch', 'delete']


class GenreViewSet(BaseCRDSlugSeachViewset):
    """Представление жанра."""

    serializer_class = GenreSerializer
    queryset = Genre.objects.all()


class CategoryViewSet(BaseCRDSlugSeachViewset):
    """Представление категории."""

    serializer_class = CategorySerializer
    queryset = Category.objects.all()


class TitleViewSet(viewsets.ModelViewSet):
    """Представление произведения."""

    queryset = Title.objects.all().annotate(
        rating=Avg('reviews__score')
    ).order_by(*Title._meta.ordering)
    permission_classes = (ReadOnlyOrAdmin,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = TitleFilter
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return TitleReadSerializer
        return TitleWriteSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Представление отзыва."""

    http_method_names = ['get', 'post', 'patch', 'delete']
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorOrModeratorOrReadOnly,)

    def get_title_or_404(self):
        return get_object_or_404(Title, id=self.kwargs['title_id'])

    def get_queryset(self):
        return self.get_title_or_404().reviews.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            title=self.get_title_or_404()
        )


class CommentViewSet(viewsets.ModelViewSet):
    """Представление комментария."""

    http_method_names = ['get', 'post', 'patch', 'delete']
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrModeratorOrReadOnly,)

    def get_review_or_404(self):
        return get_object_or_404(Review, id=self.kwargs['review_id'])

    def get_queryset(self):
        """Переопределяет метод для фильтрации комментариев."""
        return self.get_review_or_404().comments.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            review=self.get_review_or_404()
        )


def make_confirmation_code():
    return (
        ''.join(sample(
            settings.VALID_CHARS_FOR_CONFIRMATION_CODE,
            settings.MAX_LENGTH_CONFIRMATION_CODE
        ))
    )


def send_confirmation_code(user):
    """Отправляет код подтверждения на почту пользователя."""
    send_mail(
        'Код подтверждения',
        f'Ваш код подтверждения: {user.confirmation_code}',
        settings.SENDER_EMAIL,
        [user.email]
    )


class UserViewSet(viewsets.ModelViewSet):
    """Представление для операций с пользователями."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AdminOnly,)
    filter_backends = (filters.SearchFilter,)
    lookup_field = 'username'
    search_fields = ('username',)
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(
        detail=False,
        methods=['GET', 'PATCH'],
        url_path=settings.USER_PROFILE_URL,
        url_name=settings.USER_PROFILE_URL,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def profile(self, request):
        """Представление профиля текущего пользователя."""
        if request.method != 'PATCH':
            return Response(
                UserProfileSerializer(request.user).data,
                status=status.HTTP_200_OK
            )
        serializer = UserProfileSerializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@throttle_classes([UserRateThrottle])
def obtain_jwt_view(request):
    serializer = ObtainJWTSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = request.data.get('username')
    confirmation_code = request.data.get('confirmation_code')
    user = get_object_or_404(User, username=username)
    cache_key = f"confirmation_attempts_{username}"
    attempts = cache.get(cache_key, 0)
    if attempts >= settings.MAX_RETRY_ATTEMPTS:
        raise ValidationError(
            'Превышено количество попыток. Попробуйте позже.'
        )
    if user.confirmation_code != confirmation_code:
        cache.set(cache_key, attempts + 1, settings.RETRY_TIMEOUT)
        raise ValidationError(
            'Неверный код подтверждения. Запросите код ещё раз.'
        )
    cache.delete(cache_key)
    user.save()
    return Response(
        {'token': str(AccessToken.for_user(user))}, status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@throttle_classes([UserRateThrottle])
def sign_up_view(request):
    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = request.data.get('email')
    username = request.data.get('username')
    user = User.objects.filter(email=email, username=username).first()
    if user:
        if user.confirmation_code:
            minutes = settings.CONFIRMATION_CODE_LIFETIME
            time_since_last_code = timezone.now() - user.date_joined
            if time_since_last_code < timedelta(minutes):
                return Response(
                    {
                        'detail': 'Код подтверждения уже был отправлен. '
                        'Пожалуйста, проверьте вашу почту или подождите '
                        'несколько минут.'
                    },
                    status=status.HTTP_200_OK
                )
        user.confirmation_code = make_confirmation_code()
        user.save()
        send_confirmation_code(user)
        return Response(
            {'detail': 'Новый код подтверждения был отправлен на вашу почту.'},
            status=status.HTTP_200_OK
        )
    if User.objects.filter(email=email).exists():
        raise ValidationError('Email уже зарегистрирован!')
    if User.objects.filter(username=username).exists():
        user = get_object_or_404(User, username=username)
        if user.email != email:
            raise ValidationError(
                'Username уже зарегистрирован с другим email!'
            )
    user, created = User.objects.get_or_create(
        username=username,
        email=email
    )
    if not created:
        return Response(serializer.data, status=status.HTTP_200_OK)
    user.confirmation_code = make_confirmation_code()
    user.save()
    send_confirmation_code(user)
    return Response(serializer.data, status=status.HTTP_200_OK)
