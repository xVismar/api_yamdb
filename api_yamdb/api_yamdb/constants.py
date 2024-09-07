"""Константы проекта."""

MAX_LENGTH_STR = 30
MAX_LENGTH_SLUG = 50
MAX_LENGTH_NAME = 256

MAX_LENGTH_USERNAME = 150
MAX_LENGTH_EMAIL = 254
MAX_LENGTH_FIRST_NAME = 150
MAX_LENGTH_LAST_NAME = 150

USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'
LOCALIZED_USER = 'Пользователь'
LOCALIZED_MODERATOR = 'Модератор'
LOCALIZED_ADMIN = 'Админ'
ROLE_CHOICES = [
    (USER, LOCALIZED_USER),
    (MODERATOR, LOCALIZED_MODERATOR),
    (ADMIN, LOCALIZED_ADMIN),
]

MIN_VALUE_SCORE = 1
MAX_VALUE_SCORE = 10
