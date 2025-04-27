import pytest
from src.infrastructure.mock_ai_analyzer import MockAIAnalyzer
from src.domain.task import Task, Due
from src.domain.project import Project

@pytest.fixture
def analyzer():
    return MockAIAnalyzer()

@pytest.fixture
def projects():
    return [
        Project(id="work", name="Work"),
        Project(id="personal", name="Personal"),
        Project(id="shopping", name="Shopping"),
        Project(id="inbox", name="Inbox")
    ]

@pytest.fixture
def tasks():
    return [
        Task(id="1", content="Client meeting tomorrow", project_id="inbox"),
        Task(id="2", content="Buy groceries", project_id="inbox"),
        Task(id="3", content="Call mom", project_id="inbox"),
        Task(id="4", content="Random task", project_id="inbox")
    ]

def test_analyze_task_content_and_suggest_project(analyzer, tasks, projects):
    """Should correctly analyze task content and suggest appropriate project"""
    # Act
    result = analyzer.analyze_tasks([tasks[0]], projects)
    
    # Assert
    assert result.success
    suggestion = result.data[0]
    assert suggestion.task_id == "1"
    assert suggestion.suggested_project_id == "work"
    assert suggestion.confidence == 0.9
    assert "work" in suggestion.suggested_labels

def test_provide_confidence_score(analyzer, projects):
    """Should provide different confidence scores based on pattern strength"""
    # Arrange
    tasks = [
        Task(id="1", content="Client meeting", project_id="inbox"),  # Strong work match
        Task(id="2", content="Buy something", project_id="inbox"),   # Weak shopping match
    ]
    
    # Act
    result = analyzer.analyze_tasks(tasks, projects)
    
    # Assert
    assert result.success
    suggestions = result.data
    assert suggestions[0].confidence > suggestions[1].confidence
    assert suggestions[0].confidence == 0.9  # Work pattern confidence
    assert suggestions[1].confidence == 0.8  # Shopping pattern confidence

def test_provide_meaningful_explanation(analyzer, tasks, projects):
    """Should provide clear explanation for suggestion"""
    # Act
    result = analyzer.analyze_tasks([tasks[2]], projects)  # "Call mom"
    
    # Assert
    assert result.success
    suggestion = result.data[0]
    assert "personal" in suggestion.explanation.lower()
    assert "keywords" in suggestion.explanation.lower()

def test_handle_empty_task_list(analyzer, projects):
    """Should handle empty task list gracefully"""
    # Act
    result = analyzer.analyze_tasks([], projects)
    
    # Assert
    assert result.success
    assert result.data == []

def test_handle_empty_projects_list(analyzer, tasks):
    """Should return error when no projects are available"""
    # Act
    result = analyzer.analyze_tasks(tasks, [])
    
    # Assert
    assert not result.success
    assert "No projects available" in result.error

def test_respect_existing_task_patterns(analyzer, projects):
    """Should consistently categorize similar tasks"""
    # Arrange
    tasks = [
        Task(id="1", content="Team meeting", project_id="inbox"),
        Task(id="2", content="Client meeting", project_id="inbox"),
        Task(id="3", content="Board meeting", project_id="inbox"),
    ]
    
    # Act
    result = analyzer.analyze_tasks(tasks, projects)
    
    # Assert
    assert result.success
    suggestions = result.data
    assert all(s.suggested_project_id == "work" for s in suggestions)
    assert all(s.confidence == 0.9 for s in suggestions)

def test_simulate_ai_service_errors(projects):
    """Should handle AI service failures gracefully"""
    # Arrange
    analyzer = MockAIAnalyzer(should_fail=True)
    tasks = [Task(id="1", content="Test task", project_id="inbox")]
    
    # Act
    result = analyzer.analyze_tasks(tasks, projects)
    
    # Assert
    assert not result.success
    assert "AI analysis failed" in result.error

def test_multiple_keyword_matches(analyzer, projects):
    """Should choose highest confidence pattern when multiple matches exist"""
    # Arrange
    task = Task(id="1", content="Buy presentation materials for client", project_id="inbox")
    
    # Act
    result = analyzer.analyze_tasks([task], projects)
    
    # Assert
    assert result.success
    suggestion = result.data[0]
    assert suggestion.suggested_project_id == "work"  # Work has higher confidence than shopping
    assert suggestion.confidence == 0.9

def test_no_pattern_matches(analyzer, projects):
    """Should handle tasks that don't match any patterns"""
    # Arrange
    task = Task(id="1", content="Something completely random", project_id="inbox")
    
    # Act
    result = analyzer.analyze_tasks([task], projects)
    
    # Assert
    assert result.success
    suggestion = result.data[0]
    assert suggestion.suggested_project_id == "inbox"  # Default to inbox
    assert suggestion.confidence < 0.5  # Low confidence for no matches