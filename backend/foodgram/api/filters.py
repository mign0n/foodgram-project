from django_filters import rest_framework as dj_filters
from recipes.models import Tag, User
from rest_framework import filters


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
    is_favorited = dj_filters.BooleanFilter()
    is_in_shopping_cart = dj_filters.BooleanFilter()


# class RecipeFilter(FilterSet):
#     tags = ModelMultipleChoiceFilter(
#         field_name='tags__slug',
#         to_field_name='slug',
#         queryset=Tags.objects.all()
#     )
#     author = ModelMultipleChoiceFilter(
#         field_name='author__id',
#         to_field_name='id',
#         queryset=User.objects.all()
#     )
#     is_favorited = BooleanFilter(method='my_custom_filter')
#
#     class Meta:
#         model = Recipes
#         fields = (
#             'tags','author', 'is_favorited',
#         )

# def my_custom_filter(self, queryset, name, value):
#     name = 'favorite_recipes__user'
#     if value == False:
#         return queryset
#     return queryset.filter(**{
#         name: self.request.user,
#     })
