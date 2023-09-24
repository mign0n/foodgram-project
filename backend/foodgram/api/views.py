from api import serializers
from django.db.models import QuerySet
from django.utils.functional import cached_property
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as UserBaseViewSet
from recipes.models import Recipe, Tag, User
from rest_framework import mixins, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.serializers import ModelSerializer


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


class FavoriteViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.FavoriteSerializer
    lookup_field = 'recipe_id'

    @cached_property
    def _recipe(self) -> QuerySet:
        return get_object_or_404(Recipe, pk=self.kwargs.get('recipe_id'))

    def get_queryset(self) -> QuerySet:
        return self._recipe.favorite.all()

    def perform_create(self, serializer: ModelSerializer) -> None:
        serializer.save(
            recipe=self._recipe,
            owner=self.request.user,
        )
