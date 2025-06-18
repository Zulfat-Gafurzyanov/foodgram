from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from recipes.models import Ingredients, Recipes, Tags
from users.models import MyUser
from .pagination import RecipePagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    CustomUserBaseSerializer,
    UserSubscribesSerializer,
    IngredientsSerializer,
    RecipeWriteSerializer,
    RecipeReadSerializer,
    TagsSerializer
)


class CustomUserViewSet(UserViewSet):
    """
    Вьюсет для работы с пользователями.

    Эндпоинты:
    - api/users/ - доступные методы: GET, POST
    - api/users/{id}/ - доступные методы: GET
    - api/users/me/ - доступные методы: GET
    - api/users/me/avatar/ - доступные методы: PUT, DEL
    - api/users/subscriptions/ - доступные методы: GET
    - api/users/{id}/subscribe/ - доступные методы: POST, DEL
    """
    queryset = MyUser.objects.all()

    def get_serializers_class(self):
        """
        Выбираем сериализатор для обработки профиля или текущего пользователя.
        """
        if self.action in ['me', 'retrieve']:
            return CustomUserBaseSerializer
        return super().get_serializer_class()

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        url_path='subscriptions',
        url_name='subscriptions'
    )
    def subscriptions(self, request):
        """
        Возвращает пользователей, на которых подписан текущий пользователь.
        В выдачу добавляются рецепты.
        """
        user = request.user
        queryset = user.subscribers.all()
        pages = self.paginate_queryset(queryset)
        serializer = UserSubscribesSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    pagination_class = RecipePagination

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve', 'get-link'):
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @staticmethod
    def add_to(serializer_class, request, id):
        serializer = serializer_class(
            data={'user': request.user.id, 'recipe': id},
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

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
    permission_classes = (AllowAny,)


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
    permission_classes = (IsAuthorOrReadOnly,)
