from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_USER = 'user'
    ROLE_MODERATOR = 'moderator'
    ROLE_ADMIN = 'admin'
    USERS_ROLE = (
        (ROLE_USER, 'Пользователь'),
        (ROLE_MODERATOR, 'Модератор'),
        (ROLE_ADMIN, 'Админ'),
    )
    email = models.EmailField(verbose_name='Адрес электронной почты',
                              unique=True, blank=False)
    bio = models.CharField(
        verbose_name='О себе',
        max_length=500,
        blank=True,
        null=True,
    )
    role = models.CharField(
        verbose_name='Роль пользователя',
        max_length=21,
        choices=USERS_ROLE,
        default=ROLE_USER,
    )
    username = models.CharField(
        verbose_name='Username',
        null=False,
        blank=False,
        max_length=150,
        unique=True,
    )
    confirmation_code = models.CharField(
        verbose_name='Код подтверждения',
        null=False,
        blank=False,
        max_length=255
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['confirmation_code', 'username']

    @property
    def is_admin(self):
        return (self.role == self.ROLE_ADMIN
                or self.is_staff or self.is_superuser)

    @property
    def is_moderator(self):
        return self.role == self.ROLE_MODERATOR

    def __str__(self):
        return self.email

    class Meta:
        ordering = ['id']
