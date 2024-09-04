import re
from django.core.exceptions import ValidationError


def validate(self, data):
    """Проверка username на соответствие шаблону."""
    username = data.get('username')
    matching_chars = re.findall(r'[^\w.@+-]+', username)
    if matching_chars:
        raise ValidationError(
            f'Недопустимые символы в поле username: {set(matching_chars)}'
        )
    if data.get('username') == 'me':
        raise ValidationError('Использовать имя "me" запрещено')
    return data
