from drf_extra_fields.fields import Base64ImageField


from rest_framework import serializers

from recipes.models import (
    Ingredients,
    IngredientInRecipe,
    Recipes,
    Tags
)
from users.models import MyUser


class UserCreateSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = MyUser
        fields = ('username', 'email', 'first_name', 'last_name', 'avatar')

    def create(self, validated_data):
        user = MyUser(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class IngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredients
        fields = ('id', 'name', 'measurement_unit')


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = ('id', 'name', 'slug')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(
        source='ingredient.id', required=True)
    name = serializers.CharField(
        source='ingredient.name', required=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', required=True)
    amount = serializers.FloatField()

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = IngredientInRecipeSerializer(many=True)
    tags = TagsSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipes
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')
        read_only_field = ('author', )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        recipe = Recipes.objects.create(**validated_data)
        for ingredient in ingredients:
            current_ingredient, status = Ingredients.objects.get(
                **ingredient)
            IngredientInRecipe.objects.create(
                ingredient=current_ingredient, recipe=recipe)
        return recipe


class RecipesSerializer(serializers.ModelSerializer):
    ingredients = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Recipes
        fields = ('id', 'name', 'image', 'text', 'cooking_time', 'author',
                  'ingredients', 'tags')
