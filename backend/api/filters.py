from django_filters import rest_framework as dj_filters
from rest_framework import filters

from recipes.models import Tag, User


class IngredientSearchFilter(filters.SearchFilter):
    search_param = 'name'


class RecipeFilterSet(dj_filters.FilterSet):
    author = dj_filters.ModelChoiceFilter(queryset=User.objects.all())
    tags = dj_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        lookup_expr='icontains',
        queryset=Tag.objects.all(),
    )
    is_favorited = dj_filters.BooleanFilter(method='filter')
    is_in_shopping_cart = dj_filters.BooleanFilter(method='filter')

    def filter(self, queryset, name, value):
        query_lookup = {
            'is_favorited': 'favorite__author',
            'is_in_shopping_cart': 'cart__author',
        }
        if not value or not self.request.user.is_authenticated:
            return queryset
        return queryset.filter(
            **{query_lookup.get(name, ''): self.request.user},
        )
