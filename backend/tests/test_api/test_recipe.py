import json
from http import HTTPStatus
from typing import Callable

import pytest
from rest_framework.test import APIClient
from tests.utils import check_types

pytestmark = pytest.mark.django_db

ENDPOINT = '/api/recipes/'


class TestGetRecipeList:
    def test_endpoint_status_ok(self, api_client: APIClient) -> None:
        response = api_client.get(ENDPOINT)
        assert (
            response.status_code == HTTPStatus.OK
        ), f'Неверный код ответа API с эндпоинта `{ENDPOINT}`.'

    def test_no_lost_recipes(
        self,
        api_client: APIClient,
        fill_recipe_without_m2m_batch: Callable,
    ) -> None:
        fill_recipe_without_m2m_batch()
        response = api_client.get(ENDPOINT)
        content = json.loads(response.content)
        assert content.get('count') == 5, 'Неверное количество рецептов.'

    def test_correct_main_data_structure(self, api_client: APIClient) -> None:
        response = api_client.get(ENDPOINT)
        content = json.loads(response.content)
        expected = {
            'count': int,
            'next': type(None),
            'previous': type(None),
            'results': list,
        }
        assert content.keys() == expected.keys(), (
            'Ответ API с эндпоинта ' f'`{ENDPOINT}` содержит неверные ключи.'
        )
        assert check_types(content, expected), (
            f'Значение какого-либо ключа (`{expected.keys()}`) в ответе '
            f'API с эндпоинта `{ENDPOINT}` имеет неверный тип данных.',
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
        response = api_client.get(ENDPOINT)
        api_results = json.loads(response.content).get('results')[0]
        assert api_results.keys() == expected.keys(), (
            f'Данные (`results`) ответа API с эндпоинта `{ENDPOINT}` '
            'содержит неверные ключи.'
        )
        assert check_types(api_results, expected), (
            f'Значение какого-либо ключа (`{expected.keys()}`) в данных '
            f'(`results`) ответа API с эндпоинта `{ENDPOINT}` имеет '
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
        response = api_client.get(ENDPOINT)
        api_results = json.loads(response.content).get('results')
        assert (
            api_results[0].get('ingredients') == expected
        ), 'Список ингредиентов в ответе API не соответствует ожидаемому.'


class TestGetRecipe:
    def test_retrieve_recipe_with_tags(
        self,
        api_client: APIClient,
        fill_recipe_with_tags_batch: Callable,
    ) -> None:
        required_id = 3
        recipe = fill_recipe_with_tags_batch()[required_id - 1]
        tag = recipe.tags.get(pk=1)
        response = api_client.get(f'{ENDPOINT}{required_id}/')
        api_content = json.loads(response.content)
        expected = {
            'id': recipe.pk,
            'tags': [
                {
                    'id': tag.pk,
                    'name': tag.name,
                    'color': tag.color,
                    'slug': tag.slug,
                }
            ],
        }
        for key, value in expected.items():
            assert api_content.get(key) == value, (
                f'В рецепте значение `{value}` ключа `{key}` '
                f'не совпадает с ожидаемым `{api_content.get(key)}`.'
            )

    def test_retrieve_recipe_with_ingredients(
        self,
        api_client: APIClient,
        fill_recipe_with_ingredients_batch: Callable,
    ) -> None:
        required_id = 3
        ingredient = fill_recipe_with_ingredients_batch()[required_id - 1]
        recipe = ingredient.ingredientinrecipe.get().recipe
        response = api_client.get(f'{ENDPOINT}{required_id}/')
        api_content = json.loads(response.content)
        expected = {
            'id': recipe.pk,
            'tags': [],
            'author': {
                'email': recipe.author.email,
                'id': recipe.author.pk,
                'username': recipe.author.username,
                'first_name': recipe.author.first_name,
                'last_name': recipe.author.last_name,
                # 'is_subscribed': 'false',
            },
            'ingredients': [
                {
                    'id': ingredient.pk,
                    'name': ingredient.name,
                    'measurement_unit': ingredient.measurement_unit,
                    'amount': ingredient.ingredientinrecipe.get().amount,
                }
            ],
            'is_favorited': bool(recipe.favorite_count),
            'is_in_shopping_cart': bool(recipe.in_shopping_cart_count),
            'name': recipe.name,
            'image': ''.join(('http://testserver', recipe.image.url)),
            'text': recipe.text,
            'cooking_time': recipe.cooking_time,
        }
        assert api_content == expected, (
            'Хотя бы одно поле в запрошенном '
            'рецепте не соответствует ожидаем(-ым)ому.'
        )

    def test_retrive_recipe_notfound(self, api_client: APIClient) -> None:
        expected = {'detail': 'Страница не найдена.'}
        url = f'{ENDPOINT}{1}/'
        response = api_client.get(url)
        assert (
            response.status_code == HTTPStatus.NOT_FOUND
        ), f'Неверный код ответа API с эндпоинта `{url}`.'
        assert (
            json.loads(response.content) == expected
        ), 'Неверное описание ошибки 404.'


class TestPostRecipe:
    def test_create_recipe_ok(self):
        pass
