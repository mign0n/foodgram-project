from api import serializers
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as UserBaseViewSet
from recipes.models import Recipe, Tag, User
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly


class UserViewSet(UserBaseViewSet):
    queryset = User.objects.all().order_by('date_joined')


class TagViewSet(viewsets.ModelViewSet):
    pagination_class = None
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Tag.objects.all().order_by('id')
    serializer_class = serializers.TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Recipe.objects.all().order_by('-pub_date')
    serializer_class = serializers.RecipeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        'author',
        'tags',
        'is_favorited',
        'is_in_shopping_cart',
    ]
