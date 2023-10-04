import base64
from typing import OrderedDict

from django.contrib.auth.models import AbstractUser
from django.core.files.base import ContentFile
from django.db.models import Model, QuerySet
from django.utils.functional import cached_property
from djoser.serializers import UserCreateSerializer as UserCreateBaseSerializer
from djoser.serializers import UserSerializer as UserBaseSerializer
from recipes.models import (
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    Subscribe,
    Tag,
)
from rest_framework import serializers

EXTRA_FIELDS = (
    'username',
    'first_name',
    'last_name',
)


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            img_format, img_str = data.split(';base64,')
            _, ext = img_format.split('/')
            data = ContentFile(base64.b64decode(img_str), name='temp.' + ext)
        return super().to_internal_value(data)


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
        return obj.subscribe.exists()


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
        source='ingredient_id',
        read_only=True,
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


class RecipeSerializer(RecipeMinifiedSerializer):
    tags = TagSerializer(
        many=True,
        read_only=True,
    )
    author = UsersSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(
        source='ingredientinrecipe',
        many=True,
    )
    is_favorited = serializers.BooleanField(
        source='favorite_count',
        read_only=True,
    )
    is_in_shopping_cart = serializers.BooleanField(
        source='in_shopping_cart_count',
        read_only=True,
    )

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

    def validate_ingredients(
        self,
        value: list[OrderedDict],
    ) -> list[OrderedDict]:
        if not value:
            raise serializers.ValidationError(
                'The "ingredients" field must be filled in when the recipe is '
                'created.'
            )

        ingredients = self.initial_data.get('ingredients')
        if len(value) > len(
            set([ingredient.get('id') for ingredient in ingredients])
        ):
            raise serializers.ValidationError(
                'Repeating ingredients in the same recipe is unacceptable.'
            )

        for ingredient in ingredients:
            ingredient_id = ingredient.get('id')
            if not self._ingredients.filter(pk=ingredient_id).exists():
                raise serializers.ValidationError(
                    f'The ingredient with id={ingredient_id} does not exists.'
                )
        return value

    def create(self, validated_data: dict) -> Model:
        request = self.context['request']
        validated_data.pop('ingredientinrecipe')
        instance = self.Meta.model.objects.create(
            author=request.user,
            **validated_data,
        )
        instance.ingredientinrecipe.set(
            [
                IngredientInRecipe.objects.create(
                    ingredient=self._ingredients.get(pk=ingredient['id']),
                    amount=ingredient['amount'],
                    recipe=instance,
                )
                for ingredient in request.data.get('ingredients')
            ]
        )
        instance.tags.set(Tag.objects.filter(pk__in=request.data.pop('tags')))
        return instance

    def update(self, instance, validated_data):
        request = self.context['request']
        validated_data.pop('ingredientinrecipe')
        ingredients_ids = []
        for ingredient in request.data.get('ingredients'):
            (
                recipe_ingredient,
                _,
            ) = self._ingredients_in_recipe.update_or_create(
                amount=ingredient['amount'],
                ingredient=self._ingredients.get(pk=ingredient['id']),
                recipe=instance,
                defaults=ingredient,
            )
            ingredients_ids.append(recipe_ingredient.pk)
        instance.ingredients.set(ingredients_ids)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.tags.set(request.data.get('tags', instance.tags))
        instance.save()

        return instance

    def to_representation(self, instance):
        representation = super(
            RecipeSerializer,
            self,
        ).to_representation(instance)
        representation['ingredients'] = [
            {**ingredient, **amount}
            for ingredient, amount in zip(
                IngredientSerializer(
                    instance.ingredients.all(),
                    many=True,
                ).data,
                representation.pop('ingredients'),
            )
        ]
        return representation


class FavoriteSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='recipe.name', required=False)
    image = Base64ImageField(source='recipe.image', required=False)
    cooking_time = serializers.IntegerField(
        source='recipe.cooking_time',
        required=False,
    )
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Favorite
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
            'owner',
        )

    def validate(self, attrs: OrderedDict) -> OrderedDict:
        recipe_id = self.context.get('kwargs').get('recipe_id')
        if not Recipe.objects.filter(pk=recipe_id).exists():
            raise serializers.ValidationError('The object is not exists.')
        if self.Meta.model.objects.filter(
            owner__exact=attrs.get('owner'),
            recipe__exact=recipe_id,
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

    def validate_author(self, value):
        request = self.context.get('request')
        queryset = self.Meta.model.objects.filter(
            author__exact=value,
            user__exact=request.user,
        )
        if value == request.user:
            raise serializers.ValidationError(
                'You can not subscribe to yourself.'
            )
        if request.method != 'DELETE' and queryset.exists():
            raise serializers.ValidationError(
                'The fields author, user must make a unique set.'
            )
        if request.method == 'DELETE' and not queryset.exists():
            raise serializers.ValidationError('The object is not exists.')
        return value
