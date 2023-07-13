import json
from http import HTTPStatus
from typing import Callable

import pytest
from rest_framework.test import APIClient
from tests.test_api.factories import TagFactory

pytestmark = pytest.mark.django_db


class TestTagEndpoints:
    endpoint = '/api/tags/'

    def test_list(
        self,
        api_client: APIClient,
        fill_tag_batch: Callable,
    ) -> None:
        fill_tag_batch(3)
        response = api_client.get(self.endpoint)
        assert response.status_code == HTTPStatus.OK
        assert len(json.loads(response.content)) == 3

    def test_retrive_ok(self, api_client: APIClient) -> None:
        tag = TagFactory.create()
        expected = {
            'id': tag.pk,
            'name': tag.name,
            'color': tag.color,
            'slug': tag.slug,
        }
        response = api_client.get(f'{self.endpoint}{tag.pk}/')
        assert response.status_code == HTTPStatus.OK
        assert json.loads(response.content) == expected

    def test_retrive_notfound(self, api_client: APIClient) -> None:
        expected = {'detail': 'Страница не найдена.'}
        response = api_client.get(f'{self.endpoint}{1}/')
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert json.loads(response.content) == expected
