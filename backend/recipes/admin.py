from django.contrib import admin
from django.db.models import Model

from recipes import models
from recipes.models import Favorite


@admin.register(models.Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'recipe',
    )


@admin.register(models.Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'recipe',
    )


@admin.register(models.Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
    )
    list_filter = ('name',)


@admin.register(models.IngredientInRecipe)
class IngredientInRecipeAdmin(admin.ModelAdmin):
    list_display = (
        'amount',
        'ingredient',
        'recipe',
    )


@admin.register(models.Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
        'favorite_count',
    )
    list_filter = (
        'author',
        'name',
        'tags',
    )

    def favorite_count(self, instance: Model) -> int:
        return Favorite.objects.filter(recipe=instance).count()


@admin.register(models.Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'user',
    )


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'color',
        'slug',
    )
