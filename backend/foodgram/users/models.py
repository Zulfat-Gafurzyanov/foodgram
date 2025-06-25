from django.contrib.auth.models import AbstractUser
from django.db import models

from foodgram.constants import (
    MAX_LENGTH_EMAIL,
    MAX_LENGTH_FIRSTNAME,
    MAX_LENGTH_SECONDNAME,
    MAX_LENGTH_USERNAME
)


class CustomUser(AbstractUser):
    """
    Модель для хранения данных о пользователе.

    Предназначена для определения юзернейма, почты, имени, фамилии и
    аватара пользователя.
    """
    username = models.CharField(
        'юзернейм',
        max_length=MAX_LENGTH_USERNAME,
        unique=True
    )
    email = models.EmailField(
        'электронная почта',
        max_length=MAX_LENGTH_EMAIL,
        unique=True
    )
    first_name = models.CharField(
        'имя',
        max_length=MAX_LENGTH_FIRSTNAME
    )
    last_name = models.CharField(
        'фамилия',
        max_length=MAX_LENGTH_SECONDNAME
    )
    avatar = models.ImageField(
        'аватар',
        upload_to='media/users/',
        null=True,
        blank=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta:
        ordering = ['username']
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'

    def __str__(self):
        return self.username


class Subscribes(models.Model):
    """
    Модель для хранения данных о подписке.

    Связана с полем user (ForeignKey) и полем author (ForeignKey)
    модели MyUser.
    """
    user = models.ForeignKey(
        CustomUser,
        verbose_name='подписчик',
        related_name='subscribers',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        CustomUser,
        verbose_name='автор рецепта',
        related_name='subscriber',
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'подписчик'
        verbose_name_plural = 'Подписчики'
        # Уникальное ограничение, чтобы избежать подписки
        # на самого себя.
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_subscribes'
            ),
        )

    def __str__(self):
        return f'{self.user} подписался на {self.author}'
