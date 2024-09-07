import re
from datetime import date
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils.deconstruct import deconstructible


# def validate_username(attr):
#     """Проверка username на соответствие шаблону."""
#     username = attr.get('username')
#     matching_chars = re.match(r'^[\w.@+-]+\Z', username)
#     if username != 'me' and matching_chars:
#         return attr
#     raise ValidationError(
#         f'Недопустимые символы в поле username: {matching_chars} '
#         f'или использованно "me" в качестве имени пользователя.'
#     )

def validate_year(year):

    if year > date.today().year:
        raise ValidationError(
            f'Введенный год: "{year}" не может быть больше текущего '
            f'{date.today().year}.'
        )
    return year

@deconstructible
class ValidateUsername:

    def validate_username(self, username):
        """Проверка имени пользователя на соответствие шаблону."""
        if username == settings.USER_PROFILE_URL:
            raise ValidationError(
                (f'Использовать имя {settings.USER_PROFILE_URL} '
                 'в качестве username запрещено!')
            )
        matching_chars = re.findall(r'[^\w.@+-]+', username)
        if matching_chars:
            ''.join(set(matching_chars))
            raise ValidationError(
                f'Поле \'username\' содержит '
                f'недопустимые символы: {set(matching_chars)}'
            )
        return username

    def __call__(self, value):
        return self.validate_username(value)