import pytest
from django.utils import timezone
from datetime import timedelta

from tasks.models import Task, Status
from .factories import TaskFactory, CategoryFactory


@pytest.mark.django_db
class TestTaskModel:
    def test_create_task(self):
        task = TaskFactory()
        assert task.pk is not None
        assert task.status == Status.PENDING

    def test_mark_completed(self):
        task = TaskFactory(status=Status.PENDING)
        task.mark_completed()

        assert task.status == Status.COMPLETED
        assert task.completed_at is not None

    def test_is_overdue_when_past_due(self):
        task = TaskFactory(
            due_date=timezone.now().date() - timedelta(days=1),
            status=Status.PENDING
        )
        assert task.is_overdue is True

    def test_is_not_overdue_when_completed(self):
        task = TaskFactory(
            due_date=timezone.now().date() - timedelta(days=1),
            status=Status.COMPLETED
        )
        assert task.is_overdue is False

    def test_str_returns_title(self):
        task = TaskFactory(title="Test Task")
        assert str(task) == "Test Task"