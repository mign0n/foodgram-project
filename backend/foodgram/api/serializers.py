from djoser.serializers import UserCreateSerializer as UserCreateBaseSerializer
from djoser.serializers import UserSerializer as UserBaseSerializer

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
