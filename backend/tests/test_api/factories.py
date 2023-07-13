from factory import RelatedFactory, SubFactory, post_generation
from factory.django import DjangoModelFactory
from factory.faker import Faker
from recipes.models import Ingredient, IngredientInRecipe, Recipe, Tag, User
from tests.utils import generate_base64_image_string


class UserFactory(DjangoModelFactory):
    email = Faker('email')
    username = Faker('word')
    first_name = Faker('first_name', locale='ru')
    last_name = Faker('last_name', locale='ru')

    class Meta:
        model = User
        django_get_or_create = ('username',)


class IngredientFactory(DjangoModelFactory):
    name = Faker('word', locale='ru')
    measurement_unit = Faker('word', locale='ru')

    class Meta:
        model = Ingredient


class TagFactory(DjangoModelFactory):
    name = Faker('word', locale='ru')
    color = Faker('color')
    slug = Faker('slug')

    class Meta:
        model = Tag
        django_get_or_create = ('name', 'color', 'slug')


class RecipeFactory(DjangoModelFactory):
    author = SubFactory(UserFactory)
    cooking_time = Faker('random_int')
    image = generate_base64_image_string()
    name = Faker('sentence', locale='ru')
    pub_date = Faker('date_time')
    text = Faker('text', locale='ru')
    favorite_count = Faker('random_int')
    in_shopping_cart_count = Faker('random_int')

    @post_generation  # type: ignore
    def tags(self, create: bool, extracted: list, **kwargs) -> None:
        del kwargs
        if not create:
            return None
        if extracted:
            self.tags.set(extracted)

    class Meta:
        model = Recipe


class IngredientInRecipeFactory(DjangoModelFactory):
    amount = Faker('random_int')
    ingredient = SubFactory(IngredientFactory)
    recipe = SubFactory(RecipeFactory)

    class Meta:
        model = IngredientInRecipe


class RecipeWithIngredient(IngredientFactory):
    ingredient1_in_recipe = RelatedFactory(
        IngredientInRecipeFactory,
        factory_related_name='ingredient',
    )
