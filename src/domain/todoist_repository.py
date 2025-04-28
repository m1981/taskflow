from abc import ABC, abstractmethod
from typing import List
from src.domain.result import Result
from src.domain.task import Task
from src.domain.project import Project
from src.domain.task_update import TaskUpdate

class TodoistRepository(ABC):
    """Interface for Todoist data access"""
    
    @abstractmethod
    def get_inbox_tasks(self) -> Result[List[Task]]:
        """Fetch all tasks from the inbox"""
        pass
    
    @abstractmethod
    def get_projects(self) -> Result[List[Project]]:
        """Fetch all projects"""
        pass
    
    @abstractmethod
    def update_task(self, update: TaskUpdate) -> Result[bool]:
        """Update a task with the given changes"""
        pass