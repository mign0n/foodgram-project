from djoser.serializers import UserCreateSerializer as UserCreateBaseSerializer
from djoser.serializers import UserSerializer as UserBaseSerializer
from recipes.models import Recipe, Tag
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


class RecipeSerializer(serializers.ModelSerializer):
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
