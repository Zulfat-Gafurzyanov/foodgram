from django.core.exceptions import ObjectDoesNotExist
from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (
    Favorite,
    IngredientInRecipe,
    Ingredients,
    Recipes,
    ShoppingCart,
    Tags,
    UserRecipe
)
from users.models import MyUser, Subscribes


class UserSerializer(serializers.ModelSerializer):
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


class UserSubscribeSerializer(UserSerializer):
    """Сериализатор для создания подписки на пользователей."""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + (
            "recipes",
            "recipes_count",
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes = obj.recipes.all()
        limit = request.query_params.get('recipes_limit')
        if limit and limit.isdigit():
            recipes = recipes[: int(limit)]
        return RecipeShortSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class RecipeShortSerializer(serializers.ModelSerializer):
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
    amount = serializers.IntegerField(min_value=1)

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
        """
        Валидиурет список ингредиентов на ввод,
        дублирование, и наличие в базе.
        """

        if not value:
            raise serializers.ValidationError(
                'Укажите хотя бы один ингредиент для рецепта.')

        unique_ingredients = set()
        for ingredient in value:
            if ingredient['id'] in unique_ingredients:
                raise serializers.ValidationError(
                    "Ингредиенты не должны повторяться."
                )
            unique_ingredients.add(ingredient["id"])

        for ingredient in value:
            try:
                Ingredients.objects.get(id=ingredient['id'])
            except ObjectDoesNotExist:
                raise serializers.ValidationError(
                    f"Ингредиенты с id {ingredient['id']} не существует"
                )

        return value

    def validate_tags(self, value):
        """Валидиурет список тегов на ввод и дублирование"""

        if not value:
            raise serializers.ValidationError(
                'Укажите хотя бы один тег рецепта.')

        if len(value) != len(set(value)):
            raise serializers.ValidationError('Использованы одинаковые теги.')

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
        instance.ingredients_in_recipe.all().delete()
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
    author = UserSerializer(read_only=True)
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


class UserRecipeBaseSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserRecipe
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        return RecipeShortSerializer(
            instance.recipe if hasattr(instance, 'recipe') else instance,
            context=self.context,
        ).data

    def validate(self, data):
        user = self.context['request'].user
        recipe = self.context['recipe']
        if self.Meta.model.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                f'Рецепт уже в {self.Meta.model._meta.verbose_name}.'
            )
        return data


class FavoriteSerializer(UserRecipeBaseSerializer):
    class Meta:
        model = Favorite
        fields = ()


class ShoppingCartSerializer(UserRecipeBaseSerializer):
    class Meta:
        model = ShoppingCart
        fields = ()
