from django_filters.rest_framework import FilterSet, filters

from recipes.models import Recipes, Tags


class RecipeFilter(FilterSet):
    """
    Фильтр для рецептов по полям:
    - теги,
    - автор,
    - рецепт в корзине,
    - рецепт в изрбанном.
    """
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tags.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
    )
    author = filters.NumberFilter(field_name='author__id')
    is_in_shopping_cart = filters.BooleanFilter(
        method='check_recipe_in_favorite_or_cart'
    )
    is_favorited = filters.BooleanFilter(
        method='check_recipe_in_favorite_or_cart'
    )

    def check_recipe_in_favorite_or_cart(self, queryset, name, value):
        """
        - name: название поля ('is_in_shopping_cart' или 'is_favorited'),
        которое определяет, проверяется рецепт на наличие в корзине покупок
        или избранных рецептах.
        - value: булевое значение (True/False), показывающее, искать рецепты
        в выбранном месте (True) или исключить их оттуда (False).
        """
        user = self.request.user
        if user.is_anonymous:
            return queryset.none() if value else queryset
        field_mapping = {
            'is_in_shopping_cart': 'in_shopping_cart__user',
            'is_favorited': 'favorite__user',
        }
        field_name = field_mapping.get(name)

        if not field_name:
            return queryset

        if value:
            return queryset.filter(**{field_name: user})
        return queryset.exclude(**{field_name: user})

    class Meta:
        model = Recipes
        fields = ('tags', 'author', 'is_in_shopping_cart', 'is_favorited')
