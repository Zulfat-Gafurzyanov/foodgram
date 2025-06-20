from django_filters.rest_framework import FilterSet, filters
from recipes.models import Recipes, Tags


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tags.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
    )
    author = filters.NumberFilter(field_name='author__id')

    class Meta:
        model = Recipes
        fields = ('tags', 'author')
