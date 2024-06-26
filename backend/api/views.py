from django.db.models import QuerySet, Sum
from django.utils.functional import cached_property
from django_filters.rest_framework import DjangoFilterBackend
from djoser.conf import settings
from djoser.views import UserViewSet as UserBaseViewSet
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
from rest_framework.serializers import ModelSerializer, ValidationError

from api import filters, serializers
from api.filters import RecipeFilterSet
from api.permissions import IsAuthor, IsAuthorOrReadOnly
from api.renderers import CSVRecipeDataRenderer, TextRecipeDataRenderer
from recipes.models import Ingredient, Recipe, Tag, User


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

        serializer.is_valid(raise_exception=True)
        if request.method == 'POST':
            serializer.save(**serializer.validated_data)
            return Response(
                serializers.UserWithRecipesSerializer(
                    author,
                    context={'request': self.request},
                ).data,
                status=status.HTTP_201_CREATED,
            )
        author.subscribe.filter(**serializer.data).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = None
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Tag.objects.all().order_by('id')
    serializer_class = serializers.TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = None
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Ingredient.objects.all().order_by('id')
    serializer_class = serializers.IngredientSerializer
    filter_backends = (filters.IngredientSearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)
    queryset = Recipe.objects.all().order_by('-pub_date')
    serializer_class = serializers.RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilterSet
    filterset_fields = (
        'author',
        'tags',
        'is_favorited',
        'is_in_shopping_cart',
    )

    @action(
        methods=('GET',),
        detail=False,
        renderer_classes=(CSVRecipeDataRenderer, TextRecipeDataRenderer),
    )  # type: ignore
    def download_shopping_cart(self, request: Request) -> Response:
        queryset = self.get_queryset().filter(cart__author=request.user)
        serializer = serializers.CheckListSerializer(
            queryset.values(
                'ingredientinrecipe__ingredient',
                'ingredientinrecipe__ingredient__name',
                'ingredientinrecipe__ingredient__measurement_unit',
            )
            .order_by('ingredientinrecipe__ingredient')
            .annotate(total_amount=Sum('ingredientinrecipe__amount')),
            many=True,
        )
        file_name = (
            f'recipes_from_shopping_cart.{request.accepted_renderer.format}'
        )
        return Response(
            serializer.data,
            headers={
                'Content-Disposition': f'attachment; filename="{file_name}"'
            },
        )


class FavoriteViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = (IsAuthor, IsAuthenticated)
    serializer_class = serializers.FavoriteSerializer
    lookup_field = 'recipe_id'

    @cached_property
    def _recipe(self) -> QuerySet:
        return get_object_or_404(Recipe, pk=self.kwargs.get('recipe_id'))

    def get_queryset(self) -> QuerySet:
        return self._recipe.favorite.filter(author=self.request.user).all()

    def get_serializer_context(self):
        serializer_context = super().get_serializer_context()
        serializer_context['kwargs'] = self.kwargs
        return serializer_context

    def perform_create(self, serializer: ModelSerializer) -> None:
        serializer.save(
            recipe=self._recipe,
            author=self.request.user,
        )

    def destroy(
        self,
        request: Request,
        *args: tuple,
        **kwargs: dict,
    ) -> Response:
        if not self.get_queryset().exists():
            raise ValidationError('The object is not exists.')
        return super().destroy(request, *args, **kwargs)


class CartViewSet(FavoriteViewSet):
    serializer_class = serializers.CartSerializer

    def get_queryset(self) -> QuerySet:
        return self._recipe.cart.filter(author=self.request.user).all()
