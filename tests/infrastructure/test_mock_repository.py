import pytest
from src.infrastructure.mock_repository import MockTodoistRepository
from src.domain.task_update import TaskUpdate
from src.domain.task import Due

def test_get_inbox_tasks_success():
    repo = MockTodoistRepository()
    result = repo.get_inbox_tasks()
    assert result.success
    assert len(result.data) == 2
    assert all(task.project_id == "inbox" for task in result.data)

def test_get_inbox_tasks_failure():
    repo = MockTodoistRepository(should_fail=True)
    result = repo.get_inbox_tasks()
    assert not result.success
    assert "Failed to fetch inbox tasks" in result.error

def test_update_task_success():
    repo = MockTodoistRepository()
    update = TaskUpdate(content="Updated content")
    result = repo.update_task("task1", update)
    assert result.success
    assert len(repo.update_history) == 1
    assert repo.update_history[0] == ("task1", update)

def test_update_task_not_found():
    repo = MockTodoistRepository()
    update = TaskUpdate(content="Updated content")
    result = repo.update_task("non_existent", update)
    assert not result.success
    assert "not found" in result.error
    assert len(repo.update_history) == 0

def test_update_task_failure():
    repo = MockTodoistRepository(should_fail=True)
    update = TaskUpdate(content="Updated content")
    result = repo.update_task("task1", update)
    assert not result.success
    assert "Failed to update task" in result.error
    assert len(repo.update_history) == 0