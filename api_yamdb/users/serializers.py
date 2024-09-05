from django.contrib.auth.tokens import default_token_generator
from rest_framework import serializers
from rest_framework.exceptions import NotFound
from users.validators import user_validate
from django.contrib.auth import get_user_model

User = get_user_model()


class UserBaseSerializer(serializers.ModelSerializer):

    def validate(self, attrs):
        user_validate(attrs)
        return super().validate(attrs)


class ObtainJWTSerializer(serializers.Serializer):
    """Сериалайзер для получения токена пользователем."""

    username = serializers.CharField()
    confirmation_code = serializers.CharField()

    def validate(self, data):
        username = data.get('username')
        confirmation_code = data.get('confirmation_code')
        if not username or not confirmation_code:
            raise serializers.ValidationError(
                "Заполните все обязательные поля."
            )
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise NotFound("Пользователь не найден.")

        confirmation_code_check = default_token_generator.check_token(
            user, token=confirmation_code
        )
        if not confirmation_code_check:
            raise serializers.ValidationError("Нет кода прав доступа.")
        data['user'] = user
        return data


class UserMeSerializer(UserBaseSerializer):

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'role',
            'bio',
            'first_name',
            'last_name',
        )
        read_only_fields = ('id', 'role')



class UserSerializer(UserBaseSerializer):

    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'role',
            'bio',
            'first_name',
            'last_name',
        )
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True},
        }


class UserSignUpSerializer(UserBaseSerializer):

    class Meta:
        model = User
        fields = ('email', 'username')

