from dataclasses import dataclass
from typing import Optional, List
from .task import Due

@dataclass(frozen=True)
class TaskUpdate:
    """Represents possible updates that can be applied to a Task"""
    content: Optional[str] = None
    labels: Optional[List[str]] = None
    due: Optional[Due] = None
    section_id: Optional[str] = None

    def has_changes(self) -> bool:
        """
        Returns True if this update contains any changes (any field is not None)
        """
        return any([
            self.content is not None,
            self.labels is not None,
            self.due is not None,
            self.section_id is not None
        ])