import re
from datetime import date

from django.conf import settings
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.response import Response


def validate_year(year):
    if year > date.today().year:
        raise ValidationError(
            f'Введенный год "{year}" не может быть больше {date.today().year}.'
        )
    return year


def validate_username(username):
    """Проверка имени пользователя на соответствие шаблону."""
    if username is None:
        return Response(
            'Поле "username" не может быть пустым!',
            status=status.HTTP_400_BAD_REQUEST
        )
    matching_chars = re.findall(r'^[\w.@+-]', username)
    if username and not matching_chars:
        invalid_chars = ''.join(set(matching_chars))
        raise ValidationError(
            f'Поле "username" содержит недопустимые символы: {invalid_chars}!'
        )
    if username == settings.USER_PROFILE_URL:
        raise ValidationError(
            f'Использовать {username} в качестве ника запрещено!'
        )
    return username
