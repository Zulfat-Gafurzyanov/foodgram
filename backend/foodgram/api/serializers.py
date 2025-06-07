from drf_extra_fields.fields import Base64ImageField


from rest_framework import serializers

from recipes.models import (
    Ingredients,
    IngredientInRecipe,
    Recipes,
    Tags
)
from users.models import MyUser


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = MyUser
        fields = ('email', 'id', 'username', 'first_name', 'last_name')


class IngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        model = Ingredients
        fields = ('id', 'name', 'measurement_unit')


class TagsSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""
    class Meta:
        model = Tags
        fields = ('id', 'name', 'slug')


class IngredientInRecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов при создании рецепта."""
    id = serializers.IntegerField()

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')


class AmountSerializer(serializers.ModelSerializer):
    """Сериализатор для получения количества ингредиента."""
    class Meta:
        model = IngredientInRecipe
        fields = ('amount')


class IngredientInRecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для получения списка ингредиентов рецепта."""
    amount = AmountSerializer(read_only=True)

    class Meta:
        model = Ingredients
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeСreateSerializer(serializers.ModelSerializer):
    ingredients = IngredientInRecipeCreateSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tags.objects.all(),
        many=True,
    )
    image = Base64ImageField()

    class Meta:
        model = Recipes
        fields = ('ingredients', 'tags', 'image', 'name', 'text',
                  'cooking_time')

    def create(self, validated_data):
        # Создание рецепта.
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        user = self.context.get('request').user
        recipe = Recipes.objects.create(**validated_data, author=user)
        # Устанавливаем теги и добавляем ингредиенты.
        recipe.tags.set(tags)
        for ingredient in ingredients:
            ingredient_obj = Ingredients.objects.get(pk=ingredient['id'])
            amount = ingredient['amount']
            IngredientInRecipe.objects.create(
                ingredient=ingredient_obj,
                recipe=recipe,
                amount=amount
            )
        return recipe

    def update(self, instance, validated_data):
        # Обновление рецепта.
        ingredients = validated_data.pop('ingredients', [])
        tags = validated_data.pop('tags', [])

        # Обновляем остальные поля рецепта
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()  # Сохраняем изменения основного рецепта

        # Обновляем теги
        instance.tags.clear()  # Удаляем существующие теги
        if tags:
            instance.tags.add(*tags)  # Добавляем новые теги

        # Обновляем ингредиенты
        IngredientInRecipe.objects.filter(recipe=instance).delete()
        for ingredient in ingredients:
            ingredient_obj = Ingredients.objects.get(pk=ingredient['id'])
            amount = ingredient['amount']
            IngredientInRecipe.objects.create(
                ingredient=ingredient_obj,
                recipe=instance,
                amount=amount
            )
        return instance




# class UserSerializer(serializers.ModelSerializer):
#     avatar = Base64ImageField()

#     class Meta:
#         model = MyUser
#         fields = ('username', 'email', 'first_name', 'last_name', 'is_subscribed', 'avatar')

#     def create(self, validated_data):
#         user = MyUser(
#             email=validated_data['email'],
#             username=validated_data['username'],
#             first_name=validated_data['first_name'],
#             last_name=validated_data['last_name']
#         )
#         user.set_password(validated_data['password'])
#         user.save()
#         return user





# class UserSerializer(serializers.ModelSerializer):
#     avatar = Base64ImageField()

#     class Meta:
#         model = MyUser
#         fields = ('username', 'email', 'first_name', 'last_name', 'is_subscribed', 'avatar')

#     def create(self, validated_data):
#         user = MyUser(
#             email=validated_data['email'],
#             username=validated_data['username'],
#             first_name=validated_data['first_name'],
#             last_name=validated_data['last_name']
#         )
#         user.set_password(validated_data['password'])
#         user.save()
#         source='ingredient.name', required=True)
#     measurement_unit = serializers.CharField(
#         source='ingredient.measurement_unit', required=True)
#     amount = serializers.FloatField()

#     class Meta:
#         model = IngredientInRecipe
#         fields = ('id', 'name', 'measurement_unit', 'amount')
