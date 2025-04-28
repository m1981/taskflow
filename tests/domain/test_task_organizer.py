import pytest
from typing import List
from src.domain.task_organizer import TaskOrganizerService
from src.domain.result import Result, success, error
from src.domain.task import Task
from src.domain.project import Project
from src.domain.task_suggestion import TaskSuggestion
from src.domain.task_update import TaskUpdate
from src.domain.todoist_repository import TodoistRepository
from src.domain.ai_analyzer import AITaskAnalyzer
from src.domain.task_validator import TaskValidator

@pytest.fixture
def mock_repository(mocker):
    repository = mocker.Mock(spec=TodoistRepository)
    repository.get_inbox_tasks.return_value = success([
        Task(id="1", content="Test task", project_id="inbox")
    ])
    repository.get_projects.return_value = success([
        Project(id="work", name="Work", is_inbox=False)
    ])
    repository.update_task.return_value = success(True)
    return repository

@pytest.fixture
def mock_analyzer(mocker):
    analyzer = mocker.Mock(spec=AITaskAnalyzer)
    # Default behavior for non-empty task list
    analyzer.analyze_tasks.return_value = success([
        TaskSuggestion(
            task_id="1",
            suggested_project_id="work",
            confidence=0.9,
            explanation="Work-related task",
            suggested_labels=["work"]
        )
    ])
    return analyzer

@pytest.fixture
def mock_validator(mocker):
    validator = mocker.Mock(spec=TaskValidator)
    validator.validate_suggestion.return_value = True
    return validator

@pytest.fixture
def service(mock_repository, mock_analyzer, mock_validator):
    return TaskOrganizerService(mock_repository, mock_analyzer, mock_validator)

def test_get_suggestions_success(service, mock_repository, mock_analyzer):
    """Should successfully get suggestions for inbox tasks"""
    # Act
    result = service.get_suggestions()
    
    # Assert
    assert result.success
    assert len(result.data) == 1
    suggestion = result.data[0]
    assert suggestion.task_id == "1"
    assert suggestion.suggested_project_id == "work"
    
    # Verify correct interaction with dependencies
    mock_repository.get_inbox_tasks.assert_called_once()
    mock_repository.get_projects.assert_called_once()
    mock_analyzer.analyze_tasks.assert_called_once()

def test_get_suggestions_handles_empty_inbox(service, mock_repository, mock_analyzer):
    """Should handle empty inbox gracefully"""
    # Arrange
    mock_repository.get_inbox_tasks.return_value = success([])
    mock_analyzer.analyze_tasks.return_value = success([])  # Empty suggestions for empty task list
    
    # Act
    result = service.get_suggestions()
    
    # Assert
    assert result.success
    assert len(result.data) == 0

def test_get_suggestions_repository_error(service, mock_repository):
    """Should handle repository errors gracefully"""
    # Arrange
    mock_repository.get_inbox_tasks.return_value = error("API error")
    
    # Act
    result = service.get_suggestions()
    
    # Assert
    assert not result.success
    assert "Failed to fetch inbox tasks" in result.error

def test_get_suggestions_analyzer_error(service, mock_analyzer):
    """Should handle analyzer errors gracefully"""
    # Arrange
    mock_analyzer.analyze_tasks.return_value = error("Analysis failed")
    
    # Act
    result = service.get_suggestions()
    
    # Assert
    assert not result.success
    assert "Failed to analyze tasks" in result.error

def test_apply_suggestion_success(service, mock_repository, mock_validator):
    """Should successfully apply valid suggestion"""
    # Arrange
    suggestion = TaskSuggestion(
        task_id="1",
        suggested_project_id="work",
        confidence=0.9,
        explanation="Work-related task",
        suggested_labels=["work"]
    )
    
    # Act
    result = service.apply_suggestion(suggestion)
    
    # Assert
    assert result.success
    mock_validator.validate_suggestion.assert_called_once()
    mock_repository.update_task.assert_called_once()

def test_apply_suggestion_invalid_suggestion(service, mock_validator):
    """Should reject invalid suggestions"""
    # Arrange
    suggestion = TaskSuggestion(
        task_id="1",
        suggested_project_id="nonexistent",
        confidence=0.9,
        explanation="Invalid project",
        suggested_labels=[]
    )
    mock_validator.validate_suggestion.return_value = False
    
    # Act
    result = service.apply_suggestion(suggestion)
    
    # Assert
    assert not result.success
    assert "Invalid suggestion" in result.error

def test_apply_suggestion_repository_error(service, mock_repository):
    """Should handle repository errors during suggestion application"""
    # Arrange
    suggestion = TaskSuggestion(
        task_id="1",
        suggested_project_id="work",
        confidence=0.9,
        explanation="Work-related task"
    )
    mock_repository.update_task.return_value = error("Update failed")
    
    # Act
    result = service.apply_suggestion(suggestion)
    
    # Assert
    assert not result.success