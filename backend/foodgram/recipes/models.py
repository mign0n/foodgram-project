from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.dispatch import receiver

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='ингредиент',
        max_length=200,
    )
    measurement_unit = models.CharField(
        verbose_name='единица измерения',
        max_length=200,
    )

    class Meta:
        default_related_name = '%(class)s'

    def __str__(self) -> str:
        return self.name


class Tag(models.Model):
    name = models.CharField(
        verbose_name='метка',
        max_length=200,
        unique=True,
    )
    color = models.CharField(
        verbose_name='цвет метки',
        max_length=7,
        unique=True,
    )
    slug = models.SlugField(
        verbose_name='слаг',
        max_length=200,
        unique=True,
    )

    def __str__(self) -> str:
        return f'Метка {self.name}'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='автор рецепта',
    )
    cooking_time = models.IntegerField(verbose_name='время приготовления')
    image = models.ImageField(
        verbose_name='фото готового блюда',
        upload_to=settings.IMAGE_PATH,
        null=True,
        default=None,
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        related_name='recipe_ingredients',
        verbose_name='список ингредиентов рецепта',
    )
    name = models.CharField(
        verbose_name='название рецепта',
        max_length=200,
    )
    pub_date = models.DateTimeField(
        verbose_name='дата публикации',
        auto_now_add=True,
    )
    tags = models.ManyToManyField(Tag, verbose_name='список меток')
    text = models.TextField(verbose_name='описание рецепта')
    is_favorited = models.BooleanField(
        verbose_name='рецепт в списке избранных',
        default=False,
    )
    is_in_shopping_cart = models.BooleanField(
        verbose_name='рецепт в списке покупок',
        default=False,
    )
    favorite_count = models.IntegerField(default=0, blank=True)
    in_shopping_cart_count = models.IntegerField(default=0, blank=True)

    class Meta:
        ordering = ('-pub_date',)
        default_related_name = '%(class)s'

    def __str__(self) -> str:
        return f'{self.name} пользователя {self.author}'


class IngredientInRecipe(models.Model):
    amount = models.IntegerField(
        verbose_name='количество ингредиента в рецепте',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='ингредиент',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='рецепт',
    )

    class Meta:
        default_related_name = '%(class)s'

    def __str__(self) -> str:
        return (
            f'Ингредиент {self.ingredient} в рецепте {self.recipe}; '
            f'количество: {self.amount}'
        )


class Favorite(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='владелец списка избранных рецептов',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='список избранных рецептов',
    )

    class Meta:
        default_related_name = '%(class)s'

    def count_favorite(self) -> int:
        return (
            Favorite.objects.select_related(
                'owner',
                'recipe',
            )
            .filter(recipe__pk=self.recipe.pk)
            .count()
        )

    def __str__(self) -> str:
        return (
            f'Рецепт "{self.recipe.name}" в списке избранных '
            f'пользователя {self.owner}'
        )


class Cart(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='владелец списка рецептов для закупки продуктов',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='список рецептов для закупки продуктов',
    )

    class Meta:
        default_related_name = '%(class)s'

    def count_recipes(self) -> int:
        return (
            Cart.objects.select_related(
                'owner',
                'recipe',
            )
            .filter(recipe__pk=self.recipe.pk)
            .count()
        )

    def __str__(self) -> str:
        return (
            f'Рецепт "{self.recipe.name}" в списке покупок '
            f'пользователя {self.owner}'
        )


class Subscribe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='пользователь-автор',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='пользователь-подписчик',
    )

    class Meta:
        default_related_name = '%(class)s'
        constraints = [
            models.UniqueConstraint(
                fields=('author', 'user'),
                name='unique_subscribe',
            ),
            models.CheckConstraint(
                check=~models.Q(author=models.F('user')),
                name='author_is_not_user',
            ),
        ]

    def __str__(self) -> str:
        return f'{self.user} подписан на {self.author}'


@receiver(
    [
        models.signals.post_save,
        models.signals.post_delete,
    ],
    sender=Favorite,
)
def update_favorite_count(instance: Favorite, **kwargs) -> None:
    del kwargs
    Recipe.objects.filter(
        pk=instance.recipe.pk,
    ).update(favorite_count=instance.count_favorite())


@receiver(
    [
        models.signals.post_save,
        models.signals.post_delete,
    ],
    sender=Cart,
)
def update_in_cart_count(instance: Cart, **kwargs) -> None:
    del kwargs
    Recipe.objects.filter(
        pk=instance.recipe.pk,
    ).update(in_shopping_cart_count=instance.count_recipes())
