from django.core.validators import MinValueValidator
from django.db import models

from foodgram.constants import (
    MAX_LENGTH_INGREDIENT_NAME,
    MAX_LENGTH_MEASUREMENT_UNIT,
    MAX_LENGTH_RECIPE_NAME,
    MAX_LENGTH_TAG_NAME,
    MAX_LENGTH_TAG_SLUG,
    MIN_VALUE_COOKING_TIME
)
from users.models import CustomUser


class Ingredients(models.Model):
    """
    Модель для хранения Ингредиентов.

    Предназначена для определения названия ингредиента и единицы измерения.
    """
    name = models.CharField(
        'название ингредиента',
        max_length=MAX_LENGTH_INGREDIENT_NAME
    )
    measurement_unit = models.CharField(
        'единица измерения',
        max_length=MAX_LENGTH_MEASUREMENT_UNIT
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_name_measurement_unit'
            )
        ]

    def __str__(self):
        return self.name


class Tags(models.Model):
    """
    Модель для хранения Тегов.

    Предназначена для определения названия тега и слага.
    """
    name = models.CharField(
        'название тега',
        max_length=MAX_LENGTH_TAG_NAME,
        unique=True
    )
    slug = models.SlugField(
        'слаг',
        max_length=MAX_LENGTH_TAG_SLUG,
        unique=True
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'тег'
        verbose_name_plural = 'теги'

    def __str__(self):
        return self.name


class Recipes(models.Model):
    """
    Модель для хранения рецептов.

    Предназначена для определения названия рецепта, изображения,
    описания и времени приготовления (в минутах).

    Связана с моделью MyUser (ForeignKey), Ingridients (ManyToMany),
    Tags (ManyToMany).
    """

    name = models.CharField(
        'название рецепта',
        max_length=MAX_LENGTH_RECIPE_NAME
    )
    image = models.ImageField(
        'изображение рецепта',
        upload_to='media/recipes/images/'
    )
    text = models.TextField(
        'описание рецепта'
    )
    cooking_time = models.PositiveSmallIntegerField(
        'время приготовления',
        validators=[MinValueValidator(MIN_VALUE_COOKING_TIME)]
    )
    author = models.ForeignKey(
        CustomUser,
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
        ordering = ['id']
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    """
    Промежуточная модель.

    Предназначена для определения связи ManyToManyField между моделями
    Ingredients и Recipes.

    Дополнительно определяет количество ингредиента (amount).
    """
    ingredient = models.ForeignKey(
        Ingredients,
        verbose_name='ингредиент',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipes,
        verbose_name='рецепт',
        related_name='ingredients_in_recipe',
        on_delete=models.CASCADE
    )
    amount = models.PositiveSmallIntegerField('количество ингредиента')

    class Meta:
        verbose_name = 'ингредиент рецепта'
        verbose_name_plural = 'ингредиенты рецепта'
        # Уникальное ограничение, чтобы избежать дублирования
        # одного и того же ингредиента для рецепта.
        constraints = (
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_ingredient_recipe',
            ),
        )

    def __str__(self):
        return f'Ингридиент {self.recipe.name}: {self.ingredient.name}'


class UserRecipe(models.Model):
    """
    Абстрактная модель для описания полей пользователя и рецепта.
    """
    user = models.ForeignKey(
        CustomUser,
        verbose_name='пользователь',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipes,
        verbose_name='рецепт',
        on_delete=models.CASCADE
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe'
            )
        ]


class Favorite(UserRecipe):
    """
    Промежуточная модель для хранения избранных рецептов.

    Связана с моделью MyUser (ForeignKey), Recipes (ForeignKey).
    """
    class Meta:
        verbose_name = 'избранный рецепт'
        verbose_name_plural = 'избранные рецепты'
        default_related_name = 'favorite'

    def __str__(self):
        return f'{self.user.username}: избранный рецепт: {self.recipe.name}'


class ShoppingCart(UserRecipe):
    """
    Промежуточная модель для хранения списка покупок.

    Связана с моделью MyUser (ForeignKey), Recipes (ForeignKey).
    """
    class Meta:
        verbose_name = 'список покупок'
        verbose_name_plural = 'списки покупок'
        default_related_name = 'in_shopping_cart'

    def __str__(self):
        return f'{self.user.username}: в списке покупок: {self.recipe.name}'
