
import re
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from users.models import User
from rest_framework import serializers


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

