from dataclasses import dataclass
from typing import List
from src.domain.result import Result
from src.domain.task_suggestion import TaskSuggestion
from src.domain.ai_analyzer import AITaskAnalyzer
from src.domain.todoist_repository import TodoistRepository
from src.domain.task_validator import TaskValidator
from src.domain.task_update import TaskUpdate
from src.domain.task import Due

class TaskOrganizerService:
    """Service for organizing tasks using AI suggestions"""
    
    def __init__(self, repository: TodoistRepository, analyzer: AITaskAnalyzer, validator: TaskValidator):
        self._repository = repository
        self._analyzer = analyzer
        self._validator = validator

    def get_suggestions(self) -> Result[List[TaskSuggestion]]:
        """Get AI suggestions for inbox tasks"""
        tasks_result = self._repository.get_inbox_tasks()
        if not tasks_result.success:
            return Result(success=False, error=f"Failed to fetch inbox tasks: {tasks_result.error}")

        projects_result = self._repository.get_projects()
        if not projects_result.success:
            return Result(success=False, error=f"Failed to fetch projects: {projects_result.error}")

        suggestions_result = self._analyzer.analyze_tasks(tasks_result.data, projects_result.data)
        if not suggestions_result.success:
            return Result(success=False, error=f"Failed to analyze tasks: {suggestions_result.error}")

        return Result(success=True, data=suggestions_result.data)

    def apply_suggestion(self, suggestion: TaskSuggestion) -> Result[bool]:
        """Apply a single task suggestion"""
        projects_result = self._repository.get_projects()
        if not projects_result.success:
            return Result(success=False, error=f"Failed to fetch projects: {projects_result.error}")

        if not self._validator.validate_suggestion(suggestion, projects_result.data):
            return Result(success=False, error="Invalid suggestion")

        update = TaskUpdate(
            task_id=suggestion.task_id,
            project_id=suggestion.suggested_project_id,
            section_id=suggestion.suggested_section_id,
            labels=suggestion.suggested_labels,
            due=Due(string=suggestion.suggested_due) if suggestion.suggested_due else None
        )

        return self._repository.update_task(update)