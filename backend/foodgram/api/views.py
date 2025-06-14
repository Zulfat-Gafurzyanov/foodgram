from rest_framework import status, viewsets
from rest_framework.response import Response

from recipes.models import Ingredients, Recipes, Tags
from users.models import MyUser

from .pagination import RecipePagination
from .permissions import IsAuthorOrReadOnly
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
    permission_classes = [IsAuthorOrReadOnly]
    pagination_class = RecipePagination

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve', 'destroy'):
            return RecipeReadDetailDeleteSerializer
        return RecipeСreateUpdateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def destroy(self, request, *args, **kwargs):
        """
        Удаляем экземпляр рецепта.
        Доступно только авторизованным пользователям.
        """
        instance = self.get_object()  # Получаем объект из БД
        self.perform_destroy(instance)  # Удаляем объект
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
