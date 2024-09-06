from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):

    class Role(models.TextChoices):
        USER = 'user', _('User')
        ADMIN = 'admin', _('Admin')
        MODERATOR = 'moderator', _('Moderator')

    username = models.CharField(
        max_length=35,
        unique=True,
        verbose_name='Имя пользователя'
    )
    email = models.EmailField(
        max_length=35,
        unique=True,
        verbose_name='Электронная почта'
    )
    first_name = models.CharField(
        max_length=35,
        blank=True,
        null=True,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=35,
        blank=True,
        null=True,
        verbose_name='Фамилия'
    )
    bio = models.TextField(
        blank=True,
        null=True,
        verbose_name='О себе'
    )
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default='user',
        verbose_name='Роль',
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'


    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser or self.is_staff

    @property
    def is_moderator(self):
        return self.is_authenticated and self.role == 'moderator'

    @property
    def is_user(self):
        return self.role == 'user'

    def __str__(self):
        return self.username
