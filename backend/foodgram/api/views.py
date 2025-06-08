from rest_framework import viewsets

from recipes.models import Ingredients, Recipes, Tags
from users.models import MyUser

from .pagination import RecipePagination
from .serializers import (
    UserCreateSerializer,
    IngredientsSerializer,
    RecipeСreateUpdateSerializer,
    TagsSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = MyUser.objects.all()
    serializer_class = UserCreateSerializer

    # написать если методы такой то то сериализатор такой то


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    serializer_class = RecipeСreateUpdateSerializer
    pagination_class = RecipePagination

    # написать если методы такой то то сериализатор такой то


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Вьюсет для отображения ингредиентов.

    Предоставляет доступ только для чтения всех объектов модели Ingredients.

    Эндпоинты:
    - /api/ingredients/
    - /api/ingredients/{id}/
    """
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Вьюсет для отображения тегов.

    Предоставляет доступ только для чтения всех объектов модели Tags.

    Эндпоинты:
    - /api/tags/
    - /api/tags/{id}/
    """
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
