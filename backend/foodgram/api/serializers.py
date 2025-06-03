from rest_framework import serializers

from recipes.models import Ingredients, Recipes, Tags, IngredientInRecipe


class IngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredients
        fields = ('id', 'name', 'measurement_unit')


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = ('id', 'name', 'slug')


class IngredientInRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = IngredientInRecipe


class RecipesSerializer(serializers.ModelSerializer):
    ingredients = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Recipes
        fields = ('id', 'name', 'image', 'text', 'cooking_time', 'author',
                  'ingredients', 'tags')
