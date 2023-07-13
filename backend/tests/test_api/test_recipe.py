import json
from http import HTTPStatus
from typing import Callable

import pytest
from rest_framework.test import APIClient
from tests.utils import check_types

pytestmark = pytest.mark.django_db


class TestRecipeEndpoints:
    endpoint = '/api/recipes/'

    def test_endpoint_status_ok(self, api_client: APIClient) -> None:
        response = api_client.get(self.endpoint)
        assert (
            response.status_code == HTTPStatus.OK
        ), f'Неверный код ответа API с эндпоинта `{self.endpoint}`.'

    def test_no_lost_recipes(
        self,
        api_client: APIClient,
        fill_recipe_without_m2m_batch: Callable,
    ) -> None:
        fill_recipe_without_m2m_batch()
        response = api_client.get(self.endpoint)
        content = json.loads(response.content)
        assert content.get('count') == 5, 'Неверное количество рецептов.'

    def test_correct_main_data_structure(self, api_client: APIClient) -> None:
        response = api_client.get(self.endpoint)
        content = json.loads(response.content)
        expected = {
            'count': int,
            'next': type(None),
            'previous': type(None),
            'results': list,
        }
        assert content.keys() == expected.keys(), (
            'Ответ API с эндпоинта '
            f'`{self.endpoint}` содержит неверные ключи.'
        )
        assert check_types(content, expected), (
            f'Значение какого-либо ключа (`{expected.keys()}`) в ответе '
            f'API с эндпоинта `{self.endpoint}` имеет неверный тип данных.',
        )

    def test_results_keys_is_correct(
        self,
        api_client: APIClient,
        fill_recipe_without_m2m_batch: Callable,
    ) -> None:
        expected = {
            'id': int,
            'tags': list,
            'author': dict,
            'ingredients': list,
            'is_favorited': bool,
            'is_in_shopping_cart': bool,
            'name': str,
            'image': str,
            'text': str,
            'cooking_time': int,
        }
        fill_recipe_without_m2m_batch(1)
        response = api_client.get(self.endpoint)
        api_results = json.loads(response.content).get('results')[0]
        assert api_results.keys() == expected.keys(), (
            f'Данные (`results`) ответа API с эндпоинта `{self.endpoint}` '
            'содержит неверные ключи.'
        )
        assert check_types(api_results, expected), (
            f'Значение какого-либо ключа (`{expected.keys()}`) в данных '
            f'(`results`) ответа API с эндпоинта `{self.endpoint}` имеет '
            'неверный тип данных.',
        )

    def test_results_ingredients_is_correct(
        self,
        api_client: APIClient,
        fill_recipe_with_ingredients_batch: Callable,
    ) -> None:
        ingredient = fill_recipe_with_ingredients_batch(1)[0]
        expected = [
            {
                'id': ingredient.pk,
                'name': ingredient.name,
                'measurement_unit': ingredient.measurement_unit,
                'amount': ingredient.ingredientinrecipe.get().amount,
            }
        ]
        response = api_client.get(self.endpoint)
        api_results = json.loads(response.content).get('results')
        assert (
            api_results[0].get('ingredients') == expected
        ), 'Список ингредиентов в ответе API не соответствует ожидаемому.'
