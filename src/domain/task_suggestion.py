from dataclasses import dataclass
from typing import Optional, List

@dataclass(frozen=True)
class TaskSuggestion:
    """Value object representing an AI suggestion for task organization"""
    task_id: str
    suggested_project_id: str
    confidence: float
    explanation: str
    suggested_labels: Optional[List[str]] = None
    suggested_section_id: Optional[str] = None
    suggested_due: Optional[str] = None

    def __post_init__(self):
        # Ensure suggested_labels is always a list
        object.__setattr__(self, 'suggested_labels', self.suggested_labels or [])