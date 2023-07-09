import factory
from recipes.models import Tag


class TagFactory(factory.django.DjangoModelFactory):
    name = factory.faker.Faker('word', locale='ru')
    color = factory.faker.Faker('color')
    slug = factory.faker.Faker('slug')

    class Meta:
        model = Tag
