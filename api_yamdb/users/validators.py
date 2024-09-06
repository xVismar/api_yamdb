# import re
# from django.core.exceptions import ValidationError


# def user_validate(data):
#     """Проверка username на соответствие шаблону."""

#     username = data.get('username')
#     matching_chars = re.match(r'^[\w.@+-]+\Z', username)
#     if username != 'me' and matching_chars:
#         return data
#     raise ValidationError(
#         f'Недопустимые символы в поле username: {matching_chars} '
#         f'или использованно "me" в качестве имени пользователя.'
#     )
import re
from rest_framework.exceptions import ValidationError

def user_validate(data):
    username = data.get('username')
    if username is None:
        raise ValidationError('Заполните поле username.')
    matching_chars = re.findall(r'^[\w.@+-]+$', username)
    if not matching_chars:
        raise ValidationError(f'Недопустимые символы в поле username: {matching_chars}')
    if username == 'me':
        raise ValidationError('Имя пользователя "me" недопустимо.')
    return data