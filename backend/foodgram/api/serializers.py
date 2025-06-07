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
        fields = ('amount',)


class IngredientInRecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для получения списка ингредиентов рецепта."""
    amount = AmountSerializer(read_only=True)

    class Meta:
        model = Ingredients
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeСreateUpdateSerializer(serializers.ModelSerializer):
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
        """Создает рецепт."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        user = self.context.get('request').user
        recipe = Recipes.objects.create(**validated_data, author=user)
        # Устанавливаем теги и добавляем ингредиенты.
        for tag in tags:
            recipe.tags.add(tag)
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
        """Обновляет рецепт и заменяет ингредиенты и теги."""
        ingredients = validated_data.pop('ingredients', [])
        tags = validated_data.pop('tags', [])
        # Обновляем базовые поля рецепта
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        instance.save()

        # Полностью очищаем предыдущие ингредиенты и и теги,
        # заново записываем новые:
        instance.ingredients.clear()
        for ingredient in ingredients:
            ingredient_obj = Ingredients.objects.get(pk=ingredient['id'])
            amount = ingredient['amount']
            IngredientInRecipe.objects.create(
                ingredient=ingredient_obj,
                recipe=instance,
                amount=amount
            )
        for tag in tags:
            instance.tags.add(tag)

        return instance


class RecipeReadDetailDeleteSerializer(serializers.ModelSerializer):
    tags = TagsSerializer(many=True)
    # author = 
    ingredients = IngredientInRecipeReadSerializer(many=True)
    #is_favorited = 
    #is_in_shopping_cart = 
    image = Base64ImageField()

    class Meta:
        model = Recipes
        fields = ('id', 'tags', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')


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
