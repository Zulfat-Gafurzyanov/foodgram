from django.contrib.auth.models import AbstractUser
from django.db import models


class MyUser(AbstractUser):
    """
    Модель для хранения данных о пользователе.

    Предназначена для определения юзернейма, почты, имени, фамилии и
    аватара пользователя.
    """
    username = models.CharField(
        'юзернейм',
        max_length=150,
        unique=True
    )
    email = models.EmailField(
        'электронная почты',
        max_length=254,
        unique=True
    )
    first_name = models.CharField(
        'имя',
        max_length=150
    )
    last_name = models.CharField(
        'фамилия',
        max_length=150
    )
    avatar = models.ImageField(
        'аватар',
        upload_to='media/users/',
        null=True,
        blank=True
    )

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
        MyUser,
        verbose_name='подписчик',
        related_name='subscribers',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        MyUser,
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
