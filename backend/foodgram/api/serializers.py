from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (
    Favorite,
    Ingredients,
    IngredientInRecipe,
    Recipes,
    ShoppingCart,
    Tags,
)
from users.models import MyUser, Subscribes


class CustomUserBaseSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для пользователей."""
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False)

    class Meta:
        model = MyUser
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'avatar')

    def get_is_subscribed(self, obj):
        """Проверяет подписан ли текущий пользователь на этого пользователя."""
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        return Subscribes.objects.filter(user=user, author=obj).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    """Cериализатор для создания пользователей."""

    class Meta:
        model = MyUser
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'password')


class UserSubscribeSerializer(CustomUserBaseSerializer):
    """Сериализатор для создания подписки на пользователей."""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(CustomUserBaseSerializer.Meta):
        fields = (*CustomUserBaseSerializer.Meta.fields, 
                  'recipes', 'recipes_count')

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes = obj.recipes.all()
        limit = request.query_params.get('recipes_limit')
        if limit and limit.isdigit():
            recipes = recipes[: int(limit)]
        return RecipeMiniSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class RecipeMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipes
        fields = ('id', 'name', 'image', 'cooking_time')


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
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')


class RecipeСreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и изменения рецепта."""
    ingredients = IngredientInRecipeCreateSerializer(
        many=True,
        write_only=True
    )
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
        recipe = Recipes.objects.create(**validated_data)
        print(recipe)
        print(**validated_data)
        # Устанавливаем теги и добавляем ингредиенты.
        for tag in tags:
            recipe.tags.add(tag)
        for ingredient in ingredients:
            print(ingredient)
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
        instance.image = validated_data.get('image', instance.image)
        instance.save()

        # Полностью очищаем предыдущие ингредиен# написать если методы такой то то сериализатор такой тоты и и теги,
        # заново записываем новые:
        IngredientInRecipe.objects.filter(recipe=instance).delete()
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


class IngredientInRecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для получения списка ингредиентов рецепта."""
    id = serializers.ReadOnlyField(source='ingredients.id')
    name = serializers.ReadOnlyField(source='ingredients.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredients.measurement_unit'
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeReadDetailDeleteSerializer(serializers.ModelSerializer):
    """
    Сериализатор:
    - для получения списка рецептов,
    - для получения информации о рецепте,
    - для удаления рецепта.
    """

    tags = TagsSerializer(many=True, read_only=True)
    author = CustomUserBaseSerializer(read_only=True)
    ingredients = IngredientInRecipeReadSerializer(
        many=True,
        read_only=True,
        source='ingredients_in_recipe'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipes
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    def get_is_favorited(self, obj) -> bool:
        """Проверяет добавлен ли рецепт в избранное."""
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        return Favorite.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj) -> bool:
        """Проверяет добавлен ли рецепт в список покупок."""
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        return ShoppingCart.objects.filter(user=user, recipe=obj).exists()
