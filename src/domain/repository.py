from abc import ABC, abstractmethod
from typing import List
from .task import Task
from .task_update import TaskUpdate
from .result import Result

class TodoistRepository(ABC):
    """Interface for Todoist data access"""
    
    @abstractmethod
    def get_inbox_tasks(self) -> Result[List[Task]]:
        """Retrieve all tasks from the inbox"""
        pass
    
    @abstractmethod
    def update_task(self, task_id: str, update: TaskUpdate) -> Result[bool]:
        """Apply updates to a specific task"""
        pass