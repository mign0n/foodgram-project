from django_filters.rest_framework import (
    FilterSet,
    ModelChoiceFilter,
    ModelMultipleChoiceFilter,
)
from recipes.models import Tag, User
from rest_framework import filters


class IngredientSearchFilter(filters.SearchFilter):
    search_param = 'name'


class RecipeFilterSet(FilterSet):
    author = ModelChoiceFilter(queryset=User.objects.all())
    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        lookup_expr='icontains',
        queryset=Tag.objects.all(),
    )
