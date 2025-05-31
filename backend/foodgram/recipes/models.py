from django.db import models
from django.core.validators import MinValueValidator


class Ingredients(models.Model):
    """
    Модель для хранения Ингридиентов.

    Предназначена для определения названия ингридиента и единицы измерения. 
    """
    name = models.CharField(max_length=128)
    measurement_unit = models.CharField(max_length=64)

    class Meta:
        verbose_name = 'ингридиент'
        verbose_name_plural = 'Ингридиенты'


class Tags(models.Model):
    """
    Модель для хранения Тегов.

    Предназначена для определения названия тега и слага. 
    """
    name = models.CharField(max_length=32, unique=True)
    slug = models.SlugField(max_length=32, null=True, unique=True)

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'


class Recipes(models.Model):
    """
    Модель для хранения рецептов.

    Предназначена для определения названия рецепта, изображения, 
    описания и времени приготовления (в минутах).
    
    Связана с моделью User (ForeignKey), Ingridients (ManyToMany), 
    Tags (ManyToMany).
    """

    name = models.CharField(max_length=256)
    image = models.ImageField(upload_to='recipes_images/')
    text = models.TextField()
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(1)])
    #author = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True)
    ingredients = models.ManyToManyField(
        Ingredients, through = 'IngredientInRecipe')
    tags = models.ManyToManyField(Tags)

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'


class IngredientInRecipe(models.Model):
    """
    Промежуточная модель.

    Предназначена для определения связи ManyToManyField между моделями 
    Ingredients и Recipes.

    Дополнительно определяет количество ингридиента.
    """
    ingredient = models.ForeignKey(Ingredients, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()

