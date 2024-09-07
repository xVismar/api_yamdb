"""Модуль с представлениями приложения api."""

from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.response import Response

from api.filters import TitleFilter
from api.serializers import (CategorySerializer, CommentSerializer,
                             GenreSerializer, ReviewSerializer,
                             TitleReadSerializer, TitleModificateSerializer)
from reviews.models import Category, Comment, Genre, Review, Title
from api.permissions import (
    AdminOnly, IsAuthorOrModeratorOrReadOnly, ReadOnlyOrAdmin
)

from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from rest_framework import status, viewsets, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import User
from api.serializers import (
    UserSerializer, UserMeSerializer, UserSignUpSerializer, ObtainJWTSerializer
)


# class BaseViewset(viewsets.ModelViewSet):


#     def get_permissions(self):
#         return (
#             super().get_permissions()
#             if self.action not in {'list', 'retrieve'}
#             else (permissions.AllowAny(),)
#         )


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
            return TitleReadSerializer
        return TitleModificateSerializer

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


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AdminOnly,)
    http_method_names = ['get', 'post', 'patch', 'delete']
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,),
        serializer_class=UserMeSerializer
    )
    def me(self, request):
        """Обрабатывает GET запрос к users/me."""
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @me.mapping.patch
    def patch_me(self, request):
        """Обрабатывает PATCH запрос к users/me."""
        user = request.user
        data = request.data
        serializer = self.get_serializer(
            user, data=data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def user_signup_view(request):
    """Регистрация пользователя."""
    username = request.data.get('username')
    email = request.data.get('email')
    user = User.objects.filter(email=email, username=username).first()
    if user is not None:
        confirmation_code = default_token_generator.make_token(user)
        send_confirmation_code(
            email=email, confirmation_code=confirmation_code
        )
        return Response(
            {'Оповещение': 'Письмо с кодом отправлено на почту.'},
            status=status.HTTP_200_OK,
        )
    serializer = UserSignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data['username']
    email = serializer.validated_data['email']
    user = User.objects.create(username=username, email=email)
    confirmation_code = default_token_generator.make_token(user)
    send_confirmation_code(email=email, confirmation_code=confirmation_code)
    return Response(serializer.data, status=status.HTTP_200_OK)


class ObtainJWTView(APIView):
    """Отправляет JWT токен в ответ на ПОСТ запрос с кодом."""

    permission_classes = (AllowAny,)
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        serializer = ObtainJWTSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response({'token': str(refresh.access_token)})


def send_confirmation_code(email, confirmation_code):
    """Отправляем email сообщение пользователю с его кодом."""
    subject = 'Код подтверждения'
    message = f'Код подтверждения для регистрации: {confirmation_code}'
    from_email = 'api_yamdb@ya.ru'
    recipient_list = [email]
    fail_silently = True
    send_mail(subject, message, from_email, recipient_list, fail_silently)
