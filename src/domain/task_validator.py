from dataclasses import dataclass
from typing import List, Optional, Set
from src.domain.task_suggestion import TaskSuggestion
from src.domain.project import Project

class TaskValidator:
    """Validates task updates and suggestions against business rules"""
    
    def validate_suggestion(self, suggestion: TaskSuggestion, projects: List[Project]) -> bool:
        """
        Validates a task suggestion against available projects
        
        Args:
            suggestion: The suggestion to validate
            projects: List of available projects
            
        Returns:
            bool: True if suggestion is valid, False otherwise
        """
        # Validate project exists
        project_ids = {p.id for p in projects}
        if suggestion.suggested_project_id not in project_ids:
            return False
            
        # Validate confidence threshold
        if suggestion.confidence < 0.6:  # Minimum confidence threshold
            return False
            
        # Validate section belongs to project if specified
        if suggestion.suggested_section_id:
            project = next((p for p in projects if p.id == suggestion.suggested_project_id), None)
            if not project:
                return False
                
        return True