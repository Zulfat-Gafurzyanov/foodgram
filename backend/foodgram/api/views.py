from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.response import Response

from recipes.models import Ingredients, Recipes, Tags
from users.models import MyUser
from .pagination import RecipePagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    CustomUserBaseSerializer,
    CustomUserCreateSerializer,
    IngredientsSerializer,
    RecipeСreateUpdateSerializer,
    RecipeReadDetailDeleteSerializer,
    TagsSerializer
)


class UserViewSet(UserViewSet):
    queryset = MyUser.objects.all()
    serializer_class = CustomUserCreateSerializer

    # написать если методы такой то то сериализатор такой то


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    permission_classes = [IsAuthorOrReadOnly]
    pagination_class = RecipePagination

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve', 'destroy'):
            return RecipeReadDetailDeleteSerializer
        return RecipeСreateUpdateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def destroy(self, request, *args, **kwargs):
        """Удаляет рецепт."""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


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
