import pytest
from rest_framework.test import APIClient

from accounts.tests.factories import UserFactory


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def authenticated_client(client, user):
    client.force_login(user)
    return client