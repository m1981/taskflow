import pytest
from unittest.mock import create_autospec
from todoist_api_python.api import TodoistAPI
from todoist_api_python.models import Task as TodoistTask, Due as TodoistDue

from src.infrastructure.live_repository import LiveTodoistRepository
from src.domain.task_update import TaskUpdate
from src.domain.task import Due

@pytest.fixture
def mock_api():
    """Creates a properly configured mock of TodoistAPI"""
    return create_autospec(TodoistAPI, instance=True)

@pytest.fixture
def repository(monkeypatch, mock_api):
    """Creates a repository with a mocked API instance"""
    def mock_init(*args, **kwargs):
        return mock_api
    
    # Patch the TodoistAPI constructor
    monkeypatch.setattr(TodoistAPI, '__init__', lambda self, token: None)
    monkeypatch.setattr(TodoistAPI, '__new__', mock_init)
    
    return LiveTodoistRepository("fake_token")

def test_update_task_should_succeed_when_all_fields_provided(repository, mock_api):
    """
    Test that task updates with all fields are properly converted and sent to the API
    """
    # Arrange
    task_id = "123"
    update = TaskUpdate(
        content="Updated content",
        labels=["high"],
        due=Due(date="2024-01-20")
    )
    mock_api.update_task.return_value = True
    
    # Act
    result = repository.update_task(task_id, update)
    
    # Assert
    assert result.success, f"Expected successful result but got error: {result.error if hasattr(result, 'error') else 'Unknown error'}"
    mock_api.update_task.assert_called_once_with(
        task_id=task_id,
        content="Updated content",
        labels=["high"],
        due_string="2024-01-20"
    )

def test_update_task_should_fail_when_api_raises_exception(repository, mock_api):
    """
    Test that API exceptions are properly handled and returned as errors
    """
    # Arrange
    task_id = "123"
    update = TaskUpdate(content="Updated content")
    mock_api.update_task.side_effect = Exception("API Error")
    
    # Act
    result = repository.update_task(task_id, update)
    
    # Assert
    assert not result.success
    assert "Failed to update task" in result.error
    mock_api.update_task.assert_called_once_with(
        task_id=task_id,
        content="Updated content"
    )

def test_update_task_should_succeed_without_api_call_when_no_changes(repository, mock_api):
    """
    Test that empty updates succeed without making API calls
    """
    # Arrange
    task_id = "123"
    update = TaskUpdate()
    
    # Act
    result = repository.update_task(task_id, update)
    
    # Assert
    assert result.success
    mock_api.update_task.assert_not_called()