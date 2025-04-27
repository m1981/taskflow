import pytest
from datetime import datetime
from domain.task import Task, Due

class TestDue:
    def test_create_with_minimal_fields(self):
        due = Due(date="2023-12-20")
        assert due.date == "2023-12-20"
        assert due.datetime is None
        assert due.string is None

    def test_create_with_all_fields(self):
        due = Due(
            date="2023-12-20",
            datetime="2023-12-20T10:00:00Z",
            string="tomorrow at 10am"
        )
        assert due.date == "2023-12-20"
        assert due.datetime == "2023-12-20T10:00:00Z"
        assert due.string == "tomorrow at 10am"

    def test_immutability(self):
        due = Due(date="2023-12-20")
        with pytest.raises(AttributeError):
            due.date = "2023-12-21"

class TestTask:
    def test_create_with_minimal_required_fields(self):
        task = Task(
            id="123",
            content="Buy milk",
            project_id="456"
        )
        assert task.id == "123"
        assert task.content == "Buy milk"
        assert task.project_id == "456"
        assert task.labels == []
        assert task.due is None
        assert task.section_id is None

    def test_create_with_all_fields(self):
        due = Due(date="2023-12-20")
        task = Task(
            id="123",
            content="Buy milk",
            project_id="456",
            labels=["shopping", "groceries"],
            due=due,
            section_id="789"
        )
        assert task.id == "123"
        assert task.content == "Buy milk"
        assert task.project_id == "456"
        assert task.labels == ["shopping", "groceries"]
        assert task.due == due
        assert task.section_id == "789"

    def test_immutability(self):
        task = Task(id="123", content="Buy milk", project_id="456")
        with pytest.raises(AttributeError):
            task.content = "Buy coffee"

    def test_none_values_for_optional_fields(self):
        task = Task(
            id="123",
            content="Buy milk",
            project_id="456",
            labels=None,
            due=None,
            section_id=None
        )
        assert task.labels == []
        assert task.due is None
        assert task.section_id is None

    def test_labels_are_copied(self):
        labels = ["shopping"]
        task = Task(id="123", content="Buy milk", project_id="456", labels=labels)
        labels.append("groceries")
        assert task.labels == ["shopping"]