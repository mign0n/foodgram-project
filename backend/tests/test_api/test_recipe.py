import json
from http import HTTPStatus
from typing import Callable

import pytest
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


def check_types(
    checking_obj: dict[str, object],
    expected_obj: dict[str, type],
) -> bool:
    if checking_obj.keys() != expected_obj.keys():
        return False
    return all(
        [
            isinstance(value, expected_obj.get(key))  # type: ignore
            for key, value in checking_obj.items()
        ]
    )


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
        assert check_types(content, expected), (  # type: ignore
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
