from typing import OrderedDict

from django.contrib.auth.models import AbstractUser
from django.db import transaction
from django.db.models import Model, QuerySet
from django.utils.functional import cached_property
from djoser.serializers import UserCreateSerializer as UserCreateBaseSerializer
from djoser.serializers import UserSerializer as UserBaseSerializer
from rest_framework import serializers

from api.fields import Base64ImageField
from recipes.models import (
    Cart,
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    Subscribe,
    Tag,
)

EXTRA_FIELDS = (
    'username',
    'first_name',
    'last_name',
)


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )
        read_only_fields = ('id',)


class UsersSerializer(UserBaseSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserBaseSerializer.Meta):
        fields = (
            *UserBaseSerializer.Meta.fields,
            *EXTRA_FIELDS,
            'is_subscribed',
        )

    def get_is_subscribed(self, obj: AbstractUser) -> bool:
        return obj.subscribe.filter(
            user=self.context['request'].user.pk
        ).exists()


class UserCreateSerializer(UserCreateBaseSerializer):
    class Meta(UserCreateBaseSerializer.Meta):
        fields = (
            *UserCreateBaseSerializer.Meta.fields,
            *EXTRA_FIELDS,
        )


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )
        read_only_fields = ('id',)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )
        read_only_fields = (
            'name',
            'measurement_unit',
        )


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all(),
    )
    name = serializers.CharField(
        source='ingredient.get.name',
        read_only=True,
    )
    measurement_unit = serializers.CharField(
        source='ingredient.get.measurement_unit',
        read_only=True,
    )

    class Meta:
        model = IngredientInRecipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )
        read_only_fields = (
            'id',
            'recipe',
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['name'] = instance.ingredient.name
        representation[
            'measurement_unit'
        ] = instance.ingredient.measurement_unit
        return representation


class RecipeSerializer(RecipeMinifiedSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    author = UsersSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(
        source='ingredientinrecipe',
        many=True,
    )
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        read_only_fields = (
            'id',
            'tags',
            'author',
        )

    @cached_property
    def _ingredients(self) -> QuerySet:
        return Ingredient.objects.all()

    @cached_property
    def _ingredients_in_recipe(self) -> QuerySet:
        return IngredientInRecipe.objects.all()

    @cached_property
    def _tags(self) -> QuerySet:
        return Tag.objects.all()

    def get_is_favorited(self, obj) -> bool:
        return obj.favorite.filter(
            author=self.context['request'].user.pk
        ).exists()

    def get_is_in_shopping_cart(self, obj) -> bool:
        return obj.cart.filter(author=self.context['request'].user.pk).exists()

    def validate_ingredients(
        self,
        value: list[OrderedDict],
    ) -> list[OrderedDict]:
        if not value:
            raise serializers.ValidationError(
                'The "ingredients" field must be filled in when the recipe is '
                'created.'
            )

        ingredients_ids = [
            recipeingredient['ingredient'].pk for recipeingredient in value
        ]
        if len(value) > len(set(ingredients_ids)):
            raise serializers.ValidationError(
                'Repeating ingredients in the same recipe is unacceptable.'
            )

        if not self._ingredients.filter(pk__in=ingredients_ids).exists():
            raise serializers.ValidationError(
                'The ingredient does not exists.'
            )
        return value

    def validate_tags(
        self,
        value: list[OrderedDict],
    ) -> list[OrderedDict]:
        if not value:
            raise serializers.ValidationError(
                'The "tags" field must be filled in when the recipe is '
                'created.'
            )

        if len(value) > len(set([tag.pk for tag in value])):
            raise serializers.ValidationError(
                'Repeating tags in the same recipe is unacceptable.'
            )

        return value

    def validate(self, attrs: OrderedDict) -> OrderedDict:
        if not attrs.get('ingredientinrecipe'):
            raise serializers.ValidationError(
                'The "ingredients" field must be present when the recipe is '
                'updated.'
            )

        if not attrs.get('tags'):
            raise serializers.ValidationError(
                'The "tags" field must be present when the recipe is updated.'
            )
        return attrs

    def create(self, validated_data: dict) -> Model:
        request = self.context['request']
        tags = validated_data.pop('tags')
        validated_data.pop('ingredientinrecipe')
        with transaction.atomic():
            instance = self.Meta.model.objects.create(
                author=request.user,
                **validated_data,
            )
            instance.ingredientinrecipe.set(
                [
                    self._ingredients_in_recipe.create(
                        ingredient_id=ingredient['id'],
                        amount=ingredient['amount'],
                        recipe=instance,
                    )
                    for ingredient in request.data.get('ingredients')
                ]
            )
            instance.tags.set(tags)
        return instance

    def update(self, instance: Model, validated_data: dict) -> Model:
        request_data = self.context['request'].data

        validated_data.pop('ingredientinrecipe')
        with transaction.atomic():
            for ingredient in request_data.get('ingredients'):
                (
                    recipe_ingredient,
                    _,
                ) = self._ingredients_in_recipe.update_or_create(
                    recipe=instance,
                    ingredient_id=ingredient['id'],
                    defaults={
                        'amount': ingredient.get('amount'),
                        'ingredient_id': ingredient.get('id'),
                        'recipe': instance,
                    },
                )

            tags = validated_data.get('tags')
            if tags:
                instance.tags.set(tags)
                validated_data.pop('tags')

        return super().update(instance, validated_data)

    def to_representation(self, instance: Model) -> OrderedDict:
        representation = super().to_representation(instance)
        representation['tags'] = TagSerializer(
            instance.tags.all(),
            many=True,
            read_only=True,
        ).data
        return representation


class FavoriteSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='recipe.name', required=False)
    image = Base64ImageField(source='recipe.image', required=False)
    cooking_time = serializers.IntegerField(
        source='recipe.cooking_time',
        required=False,
    )
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Favorite
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
            'author',
        )

    def validate(self, attrs: OrderedDict) -> OrderedDict:
        recipe_id = self.context.get('kwargs').get('recipe_id')
        if not Recipe.objects.filter(pk=recipe_id).exists():
            raise serializers.ValidationError('The object is not exists.')
        if self.Meta.model.objects.filter(
            author=attrs.get('author'),
            recipe=recipe_id,
        ).exists():
            raise serializers.ValidationError(
                'The fields owner, recipe must make a unique set.'
            )
        return attrs


class UserWithRecipesSerializer(UsersSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UsersSerializer.Meta):
        fields = (
            *UsersSerializer.Meta.fields,
            'recipes',
            'recipes_count',
        )

    def get_recipes(self, obj: AbstractUser) -> list[dict]:
        recipes_limit = self.context.get('request').query_params.get(
            'recipes_limit'
        )
        if recipes_limit is not None and recipes_limit.isdigit():
            recipes_limit = int(recipes_limit)
        else:
            recipes_limit = None
        return RecipeMinifiedSerializer(
            obj.recipe.all()[:recipes_limit],
            many=True,
        ).data

    def get_recipes_count(self, obj: AbstractUser) -> int:
        return obj.recipe.count()


class SubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscribe
        fields = (
            'author',
            'user',
        )

    def validate_author(self, value: AbstractUser) -> AbstractUser:
        request = self.context.get('request')
        subscribe_is_exists = self.Meta.model.objects.filter(
            author=value,
            user=request.user,
        ).exists()
        if value == request.user:
            raise serializers.ValidationError(
                'You can not subscribe to yourself.'
            )
        if request.method != 'DELETE' and subscribe_is_exists:
            raise serializers.ValidationError(
                'The fields author, user must make a unique set.'
            )
        if request.method == 'DELETE' and not subscribe_is_exists:
            raise serializers.ValidationError('The object is not exists.')
        return value


class CartSerializer(FavoriteSerializer):
    class Meta:
        model = Cart
        fields = FavoriteSerializer.Meta.fields


class CheckListSerializer(serializers.Serializer):
    id = serializers.IntegerField(source='ingredientinrecipe__ingredient')
    name = serializers.CharField(source='ingredientinrecipe__ingredient__name')
    measurement_unit = serializers.CharField(
        source='ingredientinrecipe__ingredient__measurement_unit',
    )
    amount = serializers.IntegerField(source='total_amount')

    class Meta:
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )
