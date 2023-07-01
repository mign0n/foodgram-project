from djoser.serializers import UserCreateSerializer as UserCreateBaseSerializer
from djoser.serializers import UserSerializer as UserBaseSerializer
from recipes.models import Tag
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
