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


class UserSubscribesSerializer(CustomUserBaseSerializer):
    """Сериализатор для создания подписки на пользователей."""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(CustomUserBaseSerializer.Meta):
        fields = (
            *CustomUserBaseSerializer.Meta.fields,
            'recipes',
            'recipes_count'
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes = obj.recipes.all()
        page_size = request.query_params.get('recipes_page_size')
        if page_size and page_size.isdigit():
            recipes = recipes[: int(page_size)]
        return RecipeforSubscribeSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class RecipeforSubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов при отображении в подписках."""
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


class RecipeWriteSerializer(serializers.ModelSerializer):
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
        fields = ('id', 'ingredients', 'tags', 'image', 'name', 'text',
                  'cooking_time')

    def validate_ingredients(self, value):
        if len(value) != len({item['id'] for item in value}):
            raise serializers.ValidationError('Дублируются ингредиенты.')
        if not value:
            raise serializers.ValidationError(
                'Укажите хотя бы один ингредиент для рецепта.')
        return value

    def validate_tags(self, value):
        if len(value) != len(set(value)):
            raise serializers.ValidationError('Использованы одинаковые теги.')
        if not value:
            raise serializers.ValidationError(
                'Укажите хотя бы один тег рецепта.')
        return value

    def to_representation(self, instance):
        serializer = RecipeReadSerializer(
            instance, context={'request': self.context.get('request')}
        )
        return serializer.data

    def create_ingredients(self, ingredients, recipe):
        objs = []
        for ingredient in ingredients:
            objs.append(
                IngredientInRecipe(
                    recipe=recipe,
                    ingredient_id=ingredient['id'],
                    amount=ingredient['amount'],
                )
            )
        IngredientInRecipe.objects.bulk_create(objs)

    def create(self, validated_data):
        """Создает рецепт."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipes.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        """Обновляет рецепт и заменяет ингредиенты и теги."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance = super().update(instance, validated_data)
        instance.tags.set(tags)
        instance.recipe_ingredients.all().delete()
        self.create_ingredients(ingredients, instance)
        return instance


class IngredientInRecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для получения списка ингредиентов рецепта."""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
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
        source='ingredients_in_recipe',
        read_only=True
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
