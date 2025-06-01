from django.contrib.auth.models import AbstractUser
from django.db import models


class MyUser(AbstractUser):
    """
    Модель для хранения данных о пользователе.

    Предназначена для определения юзернейма, почты, имени, фамилии и 
    аватара пользователя.
    """
    username = models.CharField('юзернейм', max_length=150, unique=True) # валидация по символам  ^[\w.@+-]+\z
    email = models.EmailField('адрес электронной почты', max_length=254)
    first_name = models.CharField('имя', max_length=150) 
    last_name = models.CharField('фамилия', max_length=150)
    avatar = models.ImageField(
        'аватар', 
        upload_to='avatar/', 
        null=True,
        default=None
    )

    def __str__(self):
        return self.user


class Subscribes(models.Model):
    """
    Модель для хранения данных о пользователе.

    Предназначена для определения юзернейма, почты, имени, фамилии и 
    аватара пользователя.
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

    def __str__(self):
        return f'{self.user} подписался на {self.author}'