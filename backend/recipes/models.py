from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

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
        validators=(
            RegexValidator(
                regex='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
                message='Tag color hex code invalid.',
            ),
        ),
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
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='время приготовления',
        validators=(MinValueValidator(1),),
    )
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

    class Meta:
        ordering = ('-pub_date',)
        default_related_name = '%(class)s'

    def __str__(self) -> str:
        return f'{self.name} пользователя {self.author}'


class IngredientInRecipe(models.Model):
    amount = models.PositiveSmallIntegerField(
        verbose_name='количество ингредиента в рецепте',
        validators=(MinValueValidator(1),),
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
        constraints = [
            models.UniqueConstraint(
                fields=('ingredient', 'recipe'),
                name='unique_%(class)s',
            ),
        ]

    def __str__(self) -> str:
        return (
            f'Ингредиент {self.ingredient} в рецепте {self.recipe}; '
            f'количество: {self.amount}'
        )


class CartFavList(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='владелец списка',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='рецепт в списке',
    )

    class Meta:
        abstract = True
        default_related_name = '%(class)s'
        constraints = [
            models.UniqueConstraint(
                fields=('author', 'recipe'),
                name='unique_%(class)s_recipe',
            ),
        ]

    def __str__(self) -> str:
        return (
            f'Рецепт "{self.recipe.name}" в списке {self.__class__.__name__}s '
            f'пользователя {self.author}'
        )


class Favorite(CartFavList):
    ...


class Cart(CartFavList):
    ...


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
