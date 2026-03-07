import pytest
from django.urls import reverse
from rest_framework import status as http_status

from .factories import TaskFactory
from accounts.tests.factories import UserFactory


@pytest.mark.django_db
class TestTaskListView:
    def test_list_requires_auth(self, client):
        url = reverse('tasks:task_list')
        response = client.get(url)

        assert response.status_code == 302
        assert '/login/' in response.url

    def test_list_shows_user_tasks_only(self, client):
        user = UserFactory()
        other_user = UserFactory()

        my_task = TaskFactory(owner=user, title="My Task")
        other_task = TaskFactory(owner=other_user, title="Other Task")

        client.force_login(user)
        response = client.get(reverse('tasks:task_list'))

        assert response.status_code == 200
        assert "My Task" in response.content.decode()
        assert "Other Task" not in response.content.decode()


@pytest.mark.django_db
class TestTaskAPI:
    def test_create_task(self, api_client, user):
        api_client.force_authenticate(user)

        data = {
            'title': 'New Task',
            'description': 'Task description',
            'priority': 2,
        }

        response = api_client.post('/api/v1/tasks/', data)

        assert response.status_code == http_status.HTTP_201_CREATED
        assert response.data['title'] == 'New Task'
        assert response.data['owner'] == str(user)