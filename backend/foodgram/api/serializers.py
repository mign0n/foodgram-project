import base64

from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer as UserCreateBaseSerializer
from djoser.serializers import UserSerializer as UserBaseSerializer
from recipes.models import Ingredient, IngredientInRecipe, Recipe, Tag
from rest_framework import serializers

EXTRA_FIELDS = (
    'username',
    'first_name',
    'last_name',
)


class UsersSerializer(UserBaseSerializer):
    class Meta(UserBaseSerializer.Meta):
        fields = UserBaseSerializer.Meta.fields + EXTRA_FIELDS


class UserCreateSerializer(UserCreateBaseSerializer):
    class Meta(UserCreateBaseSerializer.Meta):
        fields = UserCreateBaseSerializer.Meta.fields + EXTRA_FIELDS


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


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            img_format, img_str = data.split(';base64,')
            _, ext = img_format.split('/')
            data = ContentFile(base64.b64decode(img_str), name='temp.' + ext)
        return super().to_internal_value(data)


class RecipeSerializer(serializers.ModelSerializer):
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
    image = Base64ImageField()

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

    def create(self, validated_data):
        request = self.context['request']
        _ = validated_data.pop('ingredientinrecipe')
        instance = self.Meta.model.objects.create(
            author=request.user,
            **validated_data,
        )
        instance.ingredientinrecipe.set(
            [
                IngredientInRecipe.objects.create(
                    ingredient=Ingredient.objects.get(pk=ingredient['id']),
                    amount=ingredient['amount'],
                )
                for ingredient in request.data.get('ingredients')
            ]
        )
        instance.tags.set(Tag.objects.filter(pk__in=request.data.pop('tags')))
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
