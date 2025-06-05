from django.db import models
from django.core.validators import MinValueValidator

from users.models import MyUser


class Ingredients(models.Model):
    """
    Модель для хранения Ингредиентов.

    Предназначена для определения названия ингредиента и единицы измерения.
    """
    name = models.CharField(
        'название ингредиента',
        max_length=128
    )
    measurement_unit = models.CharField(
        'единица измерения',
        max_length=64
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Tags(models.Model):
    """
    Модель для хранения Тегов.

    Предназначена для определения названия тега и слага.
    """
    name = models.CharField(
        'название тега',
        max_length=32,
        unique=True
    )
    slug = models.SlugField(
        'слаг',
        max_length=32,
        unique=True
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipes(models.Model):
    """
    Модель для хранения рецептов.

    Предназначена для определения названия рецепта, изображения,
    описания и времени приготовления (в минутах).

    Связана с моделью User (ForeignKey), Ingridients (ManyToMany),
    Tags (ManyToMany).
    """

    name = models.CharField(
        'название рецепта',
        max_length=256
    )
    image = models.ImageField(
        'изображение рецепта',
        upload_to='media/recipes/images/'
    )
    text = models.TextField('описание рецепта')
    cooking_time = models.PositiveIntegerField(
        'время приготовления',
        validators=[MinValueValidator(1)]
    )
    author = models.ForeignKey(
        MyUser,
        verbose_name='автор рецепта',
        related_name='recipes',
        on_delete=models.CASCADE
    )
    ingredients = models.ManyToManyField(
        Ingredients,
        verbose_name='ингредиенты',
        related_name='recipes',
        through='IngredientInRecipe',
    )
    tags = models.ManyToManyField(
        Tags,
        verbose_name='теги',
        related_name='recipes',
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    """
    Промежуточная модель.

    Предназначена для определения связи ManyToManyField между моделями
    Ingredients и Recipes.

    Дополнительно определяет количество ингредиента.
    """
    ingredient = models.ForeignKey(
        Ingredients,
        verbose_name='ингредиент',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipes,
        verbose_name='рецепт',
        on_delete=models.CASCADE
    )
    amount = models.PositiveIntegerField('количество ингредиента')

    def __str__(self):
        return f'{self.ingredient} {self.recipe}'
