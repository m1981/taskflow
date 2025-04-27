from dataclasses import dataclass
from typing import Optional, List

@dataclass(frozen=True)
class Due:
    """Value object representing a task due date"""
    date: Optional[str] = None
    datetime: Optional[str] = None
    string: Optional[str] = None

@dataclass(frozen=True)
class Task:
    """Value object representing a Todoist task"""
    id: str
    content: str
    project_id: str
    labels: List[str] = None
    due: Optional[Due] = None
    section_id: Optional[str] = None

    def __post_init__(self):
        # Ensure labels is always a list
        object.__setattr__(self, 'labels', self.labels or [])
