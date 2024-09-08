import re
from datetime import date

from django.conf import settings
from django.core.exceptions import ValidationError


def validate_year(year):

    if year > date.today().year:
        raise ValidationError(
            f'Введенный год "{year}" не может быть больше {date.today().year}.'
        )
    return year


def validate_username(username):
    """Проверка имени пользователя на соответствие шаблону."""
    if username == settings.USER_PROFILE_URL:
        raise ValidationError(
            (f'Использовать имя {settings.USER_PROFILE_URL} '
                'в качестве username запрещено!')
        )
    matching_chars = re.findall(r'[^\w.@+-]+', username)
    if matching_chars:
        raise ValidationError('Поле "username" содержит недопустимые символы!')
    return username
