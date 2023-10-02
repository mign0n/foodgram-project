from api import filters, serializers
from django.db.models import QuerySet
from django.utils.functional import cached_property
from django_filters.rest_framework import DjangoFilterBackend
from djoser.conf import settings
from djoser.views import UserViewSet as UserBaseViewSet
from recipes.models import Ingredient, Recipe, Tag, User
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import (
    BasePermission,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer


class UserViewSet(UserBaseViewSet):
    queryset = User.objects.all().order_by('date_joined')

    def get_permissions(self) -> list[BasePermission]:
        if (
            self.action == 'me'
            and self.request
            and self.request.method == 'GET'
        ):
            self.permission_classes = settings.PERMISSIONS.user_me
        return super().get_permissions()

    @cached_property
    def author(self) -> QuerySet:
        return get_object_or_404(User, pk=self.kwargs.get('id'))

    @action(methods=('GET',), detail=False)  # type: ignore
    def subscriptions(self, request: Request) -> Response:
        subscriptions = self.queryset.filter(subscribe__user=request.user)
        page = self.paginate_queryset(subscriptions)
        if page is not None:
            serializer = serializers.UserWithRecipesSerializer(
                page,
                context={'request': self.request},
                many=True,
            )
            return self.get_paginated_response(serializer.data)
        serializer = serializers.UserWithRecipesSerializer(
            subscriptions,
            context={'request': self.request},
            many=True,
        )
        return Response(serializer.data)

    @action(methods=('POST', 'DELETE'), detail=True)  # type: ignore
    def subscribe(self, request: Request, id: int) -> Response:
        author = self.author
        self.kwargs['author'] = id
        self.kwargs['user'] = self.request.user.pk
        serializer = serializers.SubscribeSerializer(
            data=self.kwargs,
            context={'request': self.request},
        )

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )
        if request.method == 'POST':
            serializer.save(**serializer.validated_data)
            return Response(
                serializers.UserWithRecipesSerializer(
                    author,
                    context={'request': self.request},
                ).data,
                status=status.HTTP_201_CREATED,
            )
        if request.method == 'DELETE':
            author.subscribe.filter(**serializer.data).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = None
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Tag.objects.all().order_by('id')
    serializer_class = serializers.TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = None
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Ingredient.objects.all().order_by('id')
    serializer_class = serializers.IngredientSerializer
    filter_backends = (filters.IngredientSearchFilter,)
    search_fields = ('^name',)


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
