"""Модуль с представлениями приложения api."""

from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import filters, permissions, status, viewsets
from rest_framework.response import Response
from api.filters import TitleFilter
from api.serializers import UserSerializer
from reviews.models import Category, Comment, Genre, Review, Title, User
from api.permissions import (
    AdminOnly, IsAuthorOrModeratorOrReadOnly, ReadOnlyOrAdmin
)
from django.core.mail import send_mail
from rest_framework import status, viewsets, filters
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from api.serializers import (
    SignUpSerializer, UserSerializer, CategorySerializer, CommentSerializer,
    ObtainJWTSerializer, UserProfileSerializer, GenreSerializer,
    ReviewSerializer, TitleSafeSerializer, TitleUnsafeSerializer
)

from django.conf import settings
from random import sample

from django.db import IntegrityError
from django.db.models import Avg
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.filters import SearchFilter
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend


class GenreViewSet(viewsets.ModelViewSet):
    """Представление жанра."""

    permission_classes = (ReadOnlyOrAdmin,)
    serializer_class = GenreSerializer
    queryset = Genre.objects.all()
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    http_method_names = ['get', 'post', 'patch', 'delete']

    def retrieve(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().retrieve(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().partial_update(request, *args, **kwargs)


class CategoryViewSet(viewsets.ModelViewSet):
    """Представление категории."""

    permission_classes = (ReadOnlyOrAdmin,)
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    http_method_names = ['get', 'post', 'patch', 'delete']

    def retrieve(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().retrieve(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().partial_update(request, *args, **kwargs)


class TitleViewSet(viewsets.ModelViewSet):
    """Представление произведения."""

    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    ).order_by('rating')
    permission_classes = (ReadOnlyOrAdmin,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = TitleFilter
    ordering_fields = ['name', 'year']
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return TitleSafeSerializer
        return TitleUnsafeSerializer

    def create(self, request, *args, **kwargs):
        """Создает новый объект Title и возвращает статус 201."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class ReviewViewSet(viewsets.ModelViewSet):
    """Представление отзыва."""

    http_method_names = ['get', 'post', 'patch', 'delete']
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorOrModeratorOrReadOnly,)

    def get_title_or_404(self):
        """Отдаёт определенное произведение или ошибку 404."""
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        """Переопределяет метод для фильтрации отзывов."""
        return self.get_title_or_404().reviews.all()

    def perform_create(self, serializer):
        """Записывает в БД отзыв и его автора."""
        serializer.save(
            author=self.request.user,
            title=self.get_title_or_404()
        )


class CommentViewSet(viewsets.ModelViewSet):
    """Представление комментария."""

    http_method_names = ['get', 'post', 'patch', 'delete']
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrModeratorOrReadOnly,)

    def get_review_or_404(self):
        """Отдает определенный отзыв или ошибку 404."""
        return get_object_or_404(Review, id=self.kwargs.get('review_id'))

    def get_queryset(self):
        """Переопределяет метод для фильтрации комментариев."""
        return self.get_review_or_404().comments.all().order_by('pub_date')

    def perform_create(self, serializer):
        """Записывает в БД комментарий и его автора."""
        serializer.save(
            author=self.request.user,
            review=self.get_review_or_404()
        )


def send_confirmation_code(user):
    """Отправляет код подтверждения на почту пользователя."""
    send_mail(
        'Код подтверждения',
        f'Ваш код подтверждения: {user.confirmation_code}',
        settings.SENDER_EMAIL,
        [user.email]
    )


class UserViewSet(ModelViewSet):
    """Представление для операций с пользователями."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AdminOnly,)
    filter_backends = (SearchFilter,)
    lookup_field = 'username'
    search_fields = ('username',)
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(
        detail=False, methods=['GET', 'PATCH'],
        url_path=settings.USER_PROFILE_URL, url_name=settings.USER_PROFILE_URL,
        permission_classes=(IsAuthenticated,)
    )
    def profile(self, request):
        """Представление профиля текущего пользователя."""
        if not request.method == 'PATCH':
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


class SignUpView(APIView):
    """Представление для регистрации новых пользователей."""

    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = request.data.get('email')
        username = request.data.get('username')
        try:
            user, _ = User.objects.get_or_create(
                username=username,
                email=email
            )
        except IntegrityError:
            raise ValidationError(
                '{field} уже зарегистрирован!'.format(
                    field=username if User.objects.filter(
                        username=username
                    ).exists() else email
                )
            )
        user.confirmation_code = ''.join(
            sample(
                settings.VALID_CHARS_FOR_CONFIRMATION_CODE,
                settings.MAX_LENGTH_CONFIRMATION_CODE
            )
        )
        user.save()
        send_confirmation_code(user)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class ObtainJWTView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = ObtainJWTSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(
            User, username=request.data.get('username')
        )
        if user.confirmation_code != request.data['confirmation_code']:
            raise ValidationError(
                'Неверный код подтверждения. Запросите код ещё раз.',
            )
        return Response(
            {'token': str(AccessToken.for_user(user))},
            status=status.HTTP_200_OK
        )