from dataclasses import FrozenInstanceError
import pytest
from datetime import datetime
from src.domain.task import Task, Due

def test_due_creation_with_minimal_fields():
    due = Due()
    assert due.date is None
    assert due.datetime is None
    assert due.string is None

def test_due_creation_with_all_fields():
    due = Due(
        date="2024-01-20",
        datetime="2024-01-20T10:00:00Z",
        string="tomorrow at 10am"
    )
    assert due.date == "2024-01-20"
    assert due.datetime == "2024-01-20T10:00:00Z"
    assert due.string == "tomorrow at 10am"

def test_due_immutability():
    due = Due(date="2024-01-20")
    with pytest.raises(FrozenInstanceError):
        due.date = "2024-01-21"

def test_task_creation_with_required_fields():
    task = Task(
        id="123",
        content="Test task",
        project_id="456"
    )
    assert task.id == "123"
    assert task.content == "Test task"
    assert task.project_id == "456"
    assert task.labels == []
    assert task.due is None
    assert task.section_id is None

def test_task_creation_with_all_fields():
    due = Due(date="2024-01-20")
    task = Task(
        id="123",
        content="Test task",
        project_id="456",
        labels=["work", "urgent"],
        due=due,
        section_id="789"
    )
    assert task.id == "123"
    assert task.content == "Test task"
    assert task.project_id == "456"
    assert task.labels == ["work", "urgent"]
    assert task.due == due
    assert task.section_id == "789"

def test_task_immutability():
    task = Task(id="123", content="Test task", project_id="456")
    with pytest.raises(FrozenInstanceError):
        task.content = "Modified task"

def test_task_handles_none_values():
    task = Task(
        id="123",
        content="Test task",
        project_id="456",
        labels=None,
        due=None,
        section_id=None
    )
    assert task.labels == []
    assert task.due is None
    assert task.section_id is None