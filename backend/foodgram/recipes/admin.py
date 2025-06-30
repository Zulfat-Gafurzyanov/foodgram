from django.contrib import admin

from foodgram.constants import EXTRA_INGREDIENT, MIN_NUM_INGREDIENT
from recipes.models import (
    Favorite,
    IngredientInRecipe,
    Ingredients,
    Recipes,
    ShoppingCart,
    Tags
)
from users.models import Subscribes


class IngredientInRecipeInline(admin.TabularInline):
    model = IngredientInRecipe
    extra = EXTRA_INGREDIENT
    min_num = MIN_NUM_INGREDIENT


@admin.register(Recipes)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'text', 'author', 'favorite_count')
    search_fields = ('name', 'author')
    list_filter = ('tags',)
    inlines = (IngredientInRecipeInline,)

    def favorite_count(self, obj):
        return obj.favorite.count()


@admin.register(Ingredients)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)


@admin.register(Tags)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


@admin.register(Subscribes)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
