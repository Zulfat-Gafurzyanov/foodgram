from django.db.models import F, Sum
from django.http import Http404, HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import (Favorite, IngredientInRecipe, Ingredients, Recipes,
                            ShoppingCart, Tags)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from users.models import MyUser, Subscribes

from .filters import IngredientFilter, RecipeFilter
from .mixins import RecipeCreateDeleteMixin
from .pagination import RecipePagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (CustomUserBaseSerializer, FavoriteSerializer,
                          IngredientsSerializer, RecipeReadSerializer,
                          RecipeWriteSerializer, ShoppingCartSerializer,
                          TagsSerializer, UserSubscribeSerializer)


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
    permission_classes = [IsAuthorOrReadOnly]
    pagination_class = RecipePagination

    def get_serializers_class(self):
        """
        Выбираем сериализатор для обработки профиля или текущего пользователя.
        """
        if self.action in ['me', 'retrieve']:
            return CustomUserBaseSerializer
        return super().get_serializer_class()

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
        url_path='subscribe',
        url_name='subscribe',
    )
    def subscribe(self, request, *args, **kwargs):
        """Реализует логику подписки и отписки на пользователя."""
        author = self.get_object()
        user = request.user

        if user == author:
            return Response(
                {'error': 'Нельзя подписаться на себя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        # Проверка наличия подписки между текущим пользователем и автором.
        subscription_exists = Subscribes.objects.filter(
            user=user, author=author).exists()

        if request.method == 'POST':
            if subscription_exists:
                return Response(
                    {'error': 'Вы уже подписаны на этого пользователя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            # Создаем подписку.
            Subscribes.objects.create(user=user, author=author)
            serializer = UserSubscribeSerializer(
                author, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            if not subscription_exists:
                return Response(
                    {'error': 'Вы не подписаны на этого пользователя'},
                    status=status.HTTP_400_BAD_REQUEST)

            Subscribes.objects.filter(user=user, author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

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
        queryset = user.subscriber.all()
        pages = self.paginate_queryset(queryset)
        serializer = UserSubscribeSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=False,
        methods=['put', 'delete'],
        url_path='me/avatar',
        url_name='me/avatar',
    )
    def avatar(self, request):
        user = request.user
        if request.method == 'PUT':
            serializer = CustomUserBaseSerializer(
                user,
                data={'avatar': request.data.get('avatar')},
                partial=True,
                context={'request': request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                {'avatar': user.avatar.url}, status=status.HTTP_200_OK
            )
        user.avatar.delete(save=True)
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipesViewSet(RecipeCreateDeleteMixin, viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    pagination_class = RecipePagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    search_fields = ('^name', 'name')

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve', 'get-link'):
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['GET'],
        url_path='get-link',
        url_name='get-link'
    )
    def get_link(self, request, pk=None):
        """Получает короткую ссылку на рецепт."""
        if not Recipes.objects.filter(pk=pk).exists():
            raise Http404('Рецепт не найден')
        url = request.build_absolute_uri(f'/recipes/{pk}/')
        return Response({'short-link': url}, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk=None):
        return self.perform_action(
            request=request,
            pk=pk,
            model=Favorite,
            serializer_class=FavoriteSerializer
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
        url_path='shopping_cart',
        url_name='shopping_cart',
    )
    def shopping_cart(self, request, pk=None):
        return self.perform_action(
            request=request,
            pk=pk,
            model=ShoppingCart,
            serializer_class=ShoppingCartSerializer,
        )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        url_path='download_shopping_cart',
        url_name='download_shopping_cart'
    )
    def download_shopping_cart(self, request):
        """Получает файл в формате .txt с общим списком ингредиентов."""
        # Получаем ингредиенты из рецептов в списке покупок пользователя.
        ingredients = IngredientInRecipe.objects.filter(
            recipe__in_shopping_cart__user=request.user
        ).values(
            name=F('ingredient__name'),
            unit=F('ingredient__measurement_unit'),
        ).annotate(
            total=Sum('amount')
        )
        # Формируем строки для каждого ингредиента
        lines = [
            f'{ingredient['name']} - {ingredient['total']} '
            f'({ingredient['unit']})'
            for ingredient in ingredients
        ]
        content = "\\n".join(lines)
        response = HttpResponse(content, content_type='text/plain')
        return response


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
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter


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
