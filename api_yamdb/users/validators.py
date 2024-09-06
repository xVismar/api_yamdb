import re
from django.core.exceptions import ValidationError


def user_validate(data):
    """Проверка username на соответствие шаблону."""

    username = data.get('username')
    matching_chars = re.findall(r'^[\w.@+-]+$', username)
    if username != 'me' and matching_chars:
        return data
    raise ValidationError(
        f'Недопустимые символы в поле username: {matching_chars} '
        f'или использованно "me" в качестве имени пользователя.'
    )
