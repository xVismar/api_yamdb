import re
from datetime import date

from django.core.exceptions import ValidationError


INVALID_USERNAMES = {'admin', 'moderator', 'user', 'me'}


def validate_year(year):
    if year > date.today().year:
        raise ValidationError(
            f'Введенный год "{year}" не может быть больше {date.today().year}.'
        )
    return year


def validate_username(username):
    """Проверка имени пользователя на соответствие шаблону."""
    if username.lower() in INVALID_USERNAMES:
        raise ValidationError(
            f'Использовать {username} в качестве ника запрещено!'
        )
    if any(char in username for char in (',', ' ')):
        raise ValidationError(
            'Нельзя использовать "," или пробелы в нике!'
        )
    matching_chars = re.findall(r'[^\w.@+-]+', username)
    if matching_chars:
        invalid_chars = ', '.join(set(matching_chars))
        raise ValidationError(
            f'Поле "username" содержит недопустимые символы: {invalid_chars}!'
        )
    return username
