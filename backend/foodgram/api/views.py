from django.db.models import Count, F, Prefetch, Sum
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.mixins import RecipeCreateDeleteMixin
from api.pagination import RecipePagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    FavoriteSerializer,
    IngredientsSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    ShoppingCartSerializer,
    TagsSerializer,
    UserSerializer,
    UserSubscribeSerializer
)
from recipes.models import (
    Favorite,
    IngredientInRecipe,
    Ingredients,
    Recipes,
    ShoppingCart,
    Tags
)
from users.models import Subscribes, User


class UserAccauntViewSet(UserViewSet):
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
    queryset = User.objects.all()
    permission_classes = [IsAuthorOrReadOnly]
    pagination_class = RecipePagination

    def get_serializers_class(self):
        """
        Выбираем сериализатор для обработки профиля или текущего пользователя.
        """
        if self.action in ['me', 'retrieve']:
            return UserSerializer
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
        subscription_data = {'user': user.id, 'author': author.id}
        try:
            serializer = UserSubscribeSerializer(
                data=subscription_data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)

            if request.method == 'POST':
                serializer.save()
                return Response(
                    {f'Подписались на {author.username}'},
                    status=status.HTTP_201_CREATED
                )
            elif request.method == 'DELETE':
                Subscribes.objects.filter(user=user, author=author).delete()
                return Response(
                    {f'Отписались от {author.username}'},
                    status=status.HTTP_204_NO_CONTENT
                )

        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

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
        authors = (
            User.objects.filter(subscriber__user=user)
            .prefetch_related(
                Prefetch(
                    'recipes',
                    queryset=Recipes.objects.order_by('-pub_date').only(
                        'id', 'name', 'image', 'cooking_time'
                    ),
                )
            )
            .annotate(recipes_count=Count('recipes'))
        )
        page = self.paginate_queryset(authors)
        if page is not None:
            serializer = UserSubscribeSerializer(
                page, many=True, context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        serializer = UserSubscribeSerializer(
            authors, many=True, context={'request': request}
        )
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['put', 'delete'],
        url_path='me/avatar',
        url_name='me/avatar',
    )
    def avatar(self, request):
        user = request.user
        if request.method == 'PUT':
            serializer = UserSerializer(
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

    @action(
        detail=True,
        methods=['GET'],
        url_path='get-link',
        url_name='get-link'
    )
    def get_link(self, request, pk=None):
        """Получает короткую ссылку на рецепт."""
        recipe = get_object_or_404(Recipes, pk=pk)
        if not Recipes.objects.filter(pk=pk).exists():
            raise Http404('Рецепт не найден')
        url = request.build_absolute_uri(f'/recipes/{recipe.pk}/')
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
            f"{ingredient['name']} - {ingredient['total']} "
            f"({ingredient['unit']})"
            for ingredient in ingredients
        ]
        content = '\\n'.join(lines)
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
    filter_backends = (IngredientFilter,)
    filterset_class = IngredientFilter
    search_fields = ('^name',)


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
