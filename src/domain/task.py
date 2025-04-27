from dataclasses import dataclass, field
from typing import Optional, List

@dataclass(frozen=True)
class Due:
    """Represents a due date for a task"""
    date: Optional[str] = None
    datetime: Optional[str] = None
    string: Optional[str] = None

@dataclass(frozen=True)
class Task:
    """Represents a Todoist task"""
    id: str
    content: str
    project_id: str
    labels: List[str] = field(default_factory=list)
    due: Optional[Due] = None
    section_id: Optional[str] = None

    def __post_init__(self):
        # Convert None labels to empty list
        object.__setattr__(self, 'labels', self.labels or [])
