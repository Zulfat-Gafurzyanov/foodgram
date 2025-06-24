from django.contrib import admin

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
    extra = 1


@admin.register(Recipes)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'favorites_count')
    search_fields = ('name', 'author__username', 'author__email')
    list_filter = ('tags',)
    inlines = (IngredientInRecipeInline,)

    def favorites_count(self, obj):
        return obj.favorite.count()


@admin.register(Ingredients)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
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
