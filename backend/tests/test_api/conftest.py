from typing import Callable

import pytest
from factory.django import DjangoModelFactory
from rest_framework.test import APIClient
from tests.test_api.factories import (
    RecipeFactory,
    RecipeWithIngredient,
    TagFactory,
)


@pytest.fixture()
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture()
def fill_tag_batch() -> Callable:
    def wrap(tag_quantity: int = 5) -> DjangoModelFactory:
        return TagFactory.create_batch(tag_quantity)

    return wrap


@pytest.fixture()
def fill_recipe_without_m2m_batch() -> Callable:
    def wrap(recipe_quantity: int = 5) -> DjangoModelFactory:
        return RecipeFactory.create_batch(recipe_quantity)

    return wrap


@pytest.fixture()
def fill_recipe_with_ingredients_batch() -> Callable:
    def wrap(recipe_quantity: int = 5) -> DjangoModelFactory:
        return RecipeWithIngredient.create_batch(recipe_quantity)

    return wrap
