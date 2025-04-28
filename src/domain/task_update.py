from dataclasses import dataclass
from typing import Optional, List
from src.domain.task import Due

@dataclass(frozen=True)
class TaskUpdate:
    """Represents changes to be applied to a task"""
    content: Optional[str] = None
    project_id: Optional[str] = None
    section_id: Optional[str] = None
    labels: Optional[List[str]] = None
    due: Optional[Due] = None
    task_id: Optional[str] = None

    def has_changes(self) -> bool:
        """Check if the update contains any changes"""
        return any([
            self.content is not None,
            self.project_id is not None,
            self.section_id is not None,
            self.labels is not None,
            self.due is not None
        ])