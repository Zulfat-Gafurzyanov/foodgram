from rest_framework import viewsets

from recipes.models import Ingredients, Recipes, Tags
from users.models import MyUser

from .pagination import RecipePagination
from .serializers import (
    UserCreateSerializer,
    IngredientsSerializer,
    RecipeСreateUpdateSerializer,
    RecipeReadDetailDeleteSerializer,
    TagsSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = MyUser.objects.all()
    serializer_class = UserCreateSerializer

    # написать если методы такой то то сериализатор такой то


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    serializer_class = RecipeСreateUpdateSerializer
    pagination_class = RecipePagination

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve', 'destroy'):
            return RecipeReadDetailDeleteSerializer
        return RecipeСreateUpdateSerializer


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
