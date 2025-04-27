import pytest
from dataclasses import FrozenInstanceError
from src.domain.task_update import TaskUpdate
from src.domain.task import Due

def test_task_update_creation_with_no_fields():
    update = TaskUpdate()
    assert update.content is None
    assert update.labels is None
    assert update.due is None
    assert update.section_id is None

def test_task_update_creation_with_all_fields():
    due = Due(date="2024-01-20")
    update = TaskUpdate(
        content="Updated content",
        labels=["work", "urgent"],
        due=due,
        section_id="789"
    )
    assert update.content == "Updated content"
    assert update.labels == ["work", "urgent"]
    assert update.due == due
    assert update.section_id == "789"

def test_task_update_immutability():
    update = TaskUpdate(content="Test content")
    with pytest.raises(FrozenInstanceError):
        update.content = "Modified content"

def test_task_update_has_changes_when_empty():
    update = TaskUpdate()
    assert not update.has_changes()

def test_task_update_has_changes_with_content():
    update = TaskUpdate(content="New content")
    assert update.has_changes()

def test_task_update_has_changes_with_labels():
    update = TaskUpdate(labels=["new-label"])
    assert update.has_changes()

def test_task_update_has_changes_with_due():
    update = TaskUpdate(due=Due(date="2024-01-20"))
    assert update.has_changes()

def test_task_update_has_changes_with_section():
    update = TaskUpdate(section_id="new-section")
    assert update.has_changes()