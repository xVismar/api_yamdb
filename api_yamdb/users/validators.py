import re
from django.core.exceptions import ValidationError


def user_validate(data):
    """Проверка username на соответствие шаблону."""
    username = data.get('username')
    matching_chars = re.findall(r'^[\w.@+-]+\Z', username)
    if username == 'me' or not matching_chars:
        raise ValidationError(

            'Недопустимые символы в поле username'
            'или использованно "me" в качестве имени пользователя.'
        )
    return data