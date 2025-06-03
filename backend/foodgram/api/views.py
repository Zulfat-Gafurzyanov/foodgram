from rest_framework import viewsets

from recipes.models import Ingredients, Recipes, Tags
from api.serializers import (
    IngredientsSerializer,
    RecipesSerializer,
    TagsSerializer
)


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Вьюсет для отображения ингредиентов.

    Предоставляет доступ только для чтения всех объектов модели Ingredients.
    """
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Вьюсет для отображения тегов.

    Предоставляет доступ только для чтения всех объектов модели Tags.
    """
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer


class RecipesViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для отображения рецептов.
    """
    queryset = Recipes.objects.all()
    serializer_class = RecipesSerializer
