from random import sample

from django.conf import settings
from django.core.mail import send_mail
from django.db import IntegrityError
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from random import randint

from api.filters import TitleFilter
from api.permissions import (
    AdminOnly, IsAuthorOrModeratorOrReadOnly, ReadOnlyOrAdmin
)
from api.serializers import (
    CategorySerializer, CommentSerializer, GenreSerializer,
    ObtainJWTSerializer, ReviewSerializer, SignUpSerializer,
    TitleModificateSerializer, TitleReadSerializer, UserProfileSerializer,
    UserSerializer
)
from reviews.models import Category, Genre, Review, Title, User
from rest_framework import viewsets

from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import AccessToken

from api.serializers import ObtainJWTSerializer, SignUpSerializer
from reviews.models import User



# class CRDSlugSearchViewSet(
#     mixins.ListModelMixin,
#     mixins.CreateModelMixin,
#     mixins.DestroyModelMixin,
#     viewsets.GenericViewSet
# ):
#     filter_backends = (SearchFilter,)
#     lookup_field = 'slug'
#     search_fields = ('name',)
#     permission_classes = (ReadOnlyOrAdmin,)


class BaseCRDViewset(
    viewsets.ViewSetMixin, generics.ListCreateAPIView, generics.DestroyAPIView
):

    permission_classes = (ReadOnlyOrAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    http_method_names = ['get', 'post', 'patch', 'delete']

    def retrieve(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

# class BaseCreateViewSet(viewsets.ModelViewSet):

#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         self.perform_create(serializer)
#         headers = self.get_success_headers(serializer.data)
#         return Response(
#             serializer.data, status=status.HTTP_201_CREATED, headers=headers
#         )


class GenreViewSet(BaseCRDViewset):
    """Представление жанра."""

    serializer_class = GenreSerializer
    queryset = Genre.objects.all()


class CategoryViewSet(BaseCRDViewset):
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
        return TitleModificateSerializer

    # def perform_create(self, serializer):
    #     """Создает новый объект Title и возвращает статус 201."""
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()

    # def perform_update(self, serializer):
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()


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


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def obtain_jwt_view(request):
    serializer = ObtainJWTSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = request.data.get('username')
    confirmation_code = request.data.get('confirmation_code')

    try:
        user = get_object_or_404(User, username=username)
    except User.DoesNotExist:
        raise ValidationError('Пользователь не найден.')

    if user.confirmation_code != confirmation_code:
        raise ValidationError('Неверный код подтверждения. Запросите код ещё раз.')

    user.is_registration_complete = True
    user.save()

    return Response({'token': str(AccessToken.for_user(user))}, status=status.HTTP_200_OK)


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
        if not created:
            return Response(serializer.data, status=status.HTTP_200_OK)
    except IntegrityError:
        field = (
            'username' if User.objects.filter(username=username).exists()
            else 'email'
        )
        raise ValidationError(f'{field} уже зарегистрирован!')
    user.confirmation_code = make_confirmation_code()
    user.save()
    pin_code = str(randint(1000, 9999))
    request.session['pin_code'] = pin_code
    send_confirmation_code(user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def resend_confirmation_code_view(request):
    pin_code = request.data.get('pin_code')
    if pin_code and pin_code == request.session.get('pin_code'):
        email = request.data.get('email')
        username = request.data.get('username')
        user = get_object_or_404(User, username=username, email=email)
        send_confirmation_code(user)
        return Response(
            {'message': 'Код подтверждения был отправлен повторно.'},
            status=status.HTTP_200_OK
        )
    else:
        raise ValidationError('Неверный пин-код.')