from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class Project:
    """Represents a Todoist project"""
    id: str
    name: str
    is_inbox: bool = False
    color: Optional[str] = None
    parent_id: Optional[str] = None