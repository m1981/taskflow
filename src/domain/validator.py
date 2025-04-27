from dataclasses import dataclass
from typing import List, Optional, Set
from .task_update import TaskUpdate
from .task import Task

@dataclass(frozen=True)
class ValidationError:
    """Represents a validation error"""
    message: str

@dataclass(frozen=True)
class ValidationContext:
    """Contains data needed for validation"""
    available_projects: Set[str]
    available_labels: Set[str]
    project_sections: dict[str, Set[str]]

class TaskValidator:
    """Validates task updates against business rules"""
    
    def __init__(self, context: ValidationContext):
        self._context = context

    def validate_update(self, update: TaskUpdate) -> Optional[ValidationError]:
        """
        Validates a task update against the current context
        Returns None if valid, ValidationError if invalid
        """
        if not update.has_changes():
            return ValidationError("Update contains no changes")

        # Validate section exists in any project
        if update.section_id is not None:
            valid_sections = set()
            for sections in self._context.project_sections.values():
                valid_sections.update(sections)
            
            if update.section_id not in valid_sections:
                return ValidationError(f"Section '{update.section_id}' does not exist in any project")

        # Validate labels exist
        if update.labels is not None:
            invalid_labels = set(update.labels) - self._context.available_labels
            if invalid_labels:
                return ValidationError(f"Invalid labels: {', '.join(invalid_labels)}")

        return None