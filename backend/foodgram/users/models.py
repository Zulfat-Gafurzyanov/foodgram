from django.contrib.auth.models import AbstractUser
from django.db import models


class MyUser(AbstractUser):
    username = models.CharField('юзернейм', max_length=150, unique=True) # валидация по символам  ^[\w.@+-]+\z
    email = models.EmailField('адрес электронной почты', max_length=254)
    first_name = models.CharField('имя', max_length=150) 
    last_name = models.CharField('фамилия', max_length=150)
    avatar = models.ImageField(
        'аватар', 
        upload_to='avatar/', 
        null=True,
        default=None)