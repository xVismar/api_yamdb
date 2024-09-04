from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from rest_framework import status, viewsets, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth import get_user_model

from users.permissions import AdminOnlyPermission
from users.serializers import (
    ObtainJWTSerializer, UserMeSerializer, UserSerializer, UserSignUpSerializer
)

User = get_user_model()


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


class UserViewSet(viewsets.ModelViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AdminOnlyPermission,)
    http_method_names = ['get', 'post', 'patch', 'delete']
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,),
        serializer_class=UserMeSerializer,
    )
    def me(self, request):
        """Обрабатывает GET запрос users/me."""
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @me.mapping.patch
    def patch_me(self, request):
        """Обрабатывает PATCH запрос users/me."""
        user = request.user
        serializer = self.get_serializer(
            user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
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