
import random

from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Avg
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from api.filters import TitleFilter
from api.permissions import (
    AdminOnly, IsAuthorOrModeratorOrReadOnly, ReadOnlyOrAdmin
)
from reviews.models import Category, Genre, Review, Title, User
from api.serializers import (
    CategorySerializer, CommentSerializer, GenreSerializer,
    ObtainJWTSerializer, ReviewSerializer, SignUpSerializer,
    TitleReadSerializer, TitleWriteSerializer,
    UserSerializer, UserProfileSerializer
)


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


def make_and_send_confirmation_code(user, serializer):
    user.confirmation_code = ''.join(
        random.choices(
            settings.VALID_CHARS_FOR_CONFIRMATION_CODE,
            k=settings.MAX_LENGTH_CONFIRMATION_CODE
        )
    )
    user.save()
    send_mail(
        'Код подтверждения',
        f'Ваш код подтверждения: {user.confirmation_code}',
        settings.SENDER_EMAIL,
        [user.email]
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


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
def sign_up_view(request):
    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = request.data.get('email')
    username = request.data.get('username')
    try:
        user, created = User.objects.get_or_create(
            username=username,
            email=email
        )
    except IntegrityError:
        field = (
            email if User.objects.filter(email=email).exists()
            else username
        )
        raise ValidationError(f'{field} уже зарегистрирован!')
    if not created:
        if user.confirmation_code == settings.INVALID_CONFIRMATION_CODE:
            raise ValidationError('Пользователь уже зарегистрирован.')
    return make_and_send_confirmation_code(user, serializer)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def obtain_jwt_view(request):
    serializer = ObtainJWTSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = request.data.get('username')
    user = get_object_or_404(User, username=username)
    if user.confirmation_code != request.data['confirmation_code']:
        user.confirmation_code = settings.INVALID_CONFIRMATION_CODE
        user.save()
        raise ValidationError('Неверный код подтверждения.')
    return Response(
        {'token': str(AccessToken.for_user(user))},
        status=status.HTTP_200_OK
    )
