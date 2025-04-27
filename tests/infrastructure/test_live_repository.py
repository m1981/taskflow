import pytest
from unittest.mock import Mock, patch
from todoist_api_python.models import Task as TodoistTask, Due as TodoistDue

from src.infrastructure.live_repository import LiveTodoistRepository
from src.domain.task_update import TaskUpdate
from src.domain.task import Due

@pytest.fixture
def mock_todoist_api():
    with patch('todoist_api_python.api.TodoistAPI', autospec=True) as mock:
        api_instance = Mock()
        mock.return_value = api_instance
        # Set up default successful responses
        api_instance.get_tasks = Mock(return_value=[])
        api_instance.update_task = Mock(return_value=True)
        yield api_instance

@pytest.fixture
def repository(mock_todoist_api):
    return LiveTodoistRepository("fake_token")

def test_get_inbox_tasks_success(repository, mock_todoist_api):
    # Setup mock response
    mock_due = TodoistDue(
        date="2024-01-20",
        is_recurring=False,
        string="Jan 20",
        datetime=None,
        timezone=None
    )
    
    mock_task = TodoistTask(
        id="123",
        content="Test task",
        project_id="inbox",
        labels=["test"],
        due=mock_due,
        section_id=None,
        parent_id=None,
        order=1,
        priority=1,
        url="https://todoist.com/showTask?id=123",
        comment_count=0,
        created_at="2024-01-19T10:00:00Z",
        creator_id="user123",
        assignee_id=None,
        assigner_id=None,
        duration=None,
        is_completed=False,
        description=""
    )
    
    # Set up the mock to return our task
    mock_todoist_api.get_tasks = Mock(return_value=[mock_task])

    # Execute
    result = repository.get_inbox_tasks()

    # Verify
    assert result.success
    assert len(result.data) == 1
    task = result.data[0]
    assert task.id == '123'
    assert task.content == 'Test task'
    assert task.project_id == 'inbox'
    assert task.labels == ['test']
    assert task.due.date == '2024-01-20'

    # Verify the mock was called with correct filter
    mock_todoist_api.get_tasks.assert_called_once_with(filter="inbox")

def test_get_inbox_tasks_api_error(repository, mock_todoist_api):
    mock_todoist_api.get_tasks = Mock(side_effect=Exception("API Error"))
    result = repository.get_inbox_tasks()
    assert not result.success
    assert "Failed to fetch inbox tasks" in result.error

def test_update_task_success(repository, mock_todoist_api):
    # Setup
    update = TaskUpdate(
        content="Updated content",
        labels=["high"],
        due=Due(date="2024-01-20")
    )
    
    # Execute
    result = repository.update_task("123", update)
    
    # Verify
    assert result.success
    mock_todoist_api.update_task.assert_called_once_with(
        task_id="123",
        content="Updated content",
        labels=["high"],
        due_string="2024-01-20"
    )

def test_update_task_api_error(repository, mock_todoist_api):
    # Setup
    mock_todoist_api.update_task = Mock(side_effect=Exception("API Error"))
    update = TaskUpdate(content="Updated content")
    
    # Execute
    result = repository.update_task("123", update)
    
    # Verify
    assert not result.success
    assert "Failed to update task" in result.error

def test_update_task_no_changes(repository, mock_todoist_api):
    update = TaskUpdate()
    result = repository.update_task("123", update)
    assert result.success
    mock_todoist_api.update_task.assert_not_called()