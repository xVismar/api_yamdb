import re

from django.core.exceptions import ValidationError
from rest_framework.exceptions import ValidationError


def validate_username(attr):
    """Проверка username на соответствие шаблону."""
    username = attr.get('username')
    matching_chars = re.match(r'^[\w.@+-]+\Z', username)
    if username != 'me' and matching_chars:
        return attr
    raise ValidationError(
        f'Недопустимые символы в поле username: {matching_chars} '
        f'или использованно "me" в качестве имени пользователя.'
    )
