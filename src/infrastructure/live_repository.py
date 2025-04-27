import time
from typing import List, Optional, TypeVar, Callable, Any
from functools import wraps
from todoist_api_python.api import TodoistAPI
from todoist_api_python.models import Task as TodoistTask
from todoist_api_python.models import Project as TodoistProject

from src.domain.repository import TodoistRepository
from src.domain.repository_config import RepositoryConfig
from src.domain.task import Task, Due
from src.domain.task_update import TaskUpdate
from src.domain.result import Result, success, error

T = TypeVar('T')

def with_retries(operation: str) -> Callable:
    """Decorator to add retry logic to repository operations"""
    def decorator(func: Callable[..., Result[T]]) -> Callable[..., Result[T]]:
        @wraps(func)
        def wrapper(self: 'LiveTodoistRepository', *args: Any, **kwargs: Any) -> Result[T]:
            last_error = None
            for attempt in range(self.config.max_retries):
                try:
                    return func(self, *args, **kwargs)
                except Exception as e:
                    last_error = str(e)
                    if attempt < self.config.max_retries - 1:
                        time.sleep(self.config.retry_delay)
            return error(f"Failed to {operation} after {self.config.max_retries} attempts: {last_error}")
        return wrapper
    return decorator

class LiveTodoistRepository(TodoistRepository):
    """Live implementation of TodoistRepository using the Todoist API"""
    
    def __init__(self, api_token: str, config: Optional[RepositoryConfig] = None):
        self._api = TodoistAPI(api_token)
        self.config = config or RepositoryConfig()

    @with_retries("fetch inbox tasks")
    def get_inbox_tasks(self) -> Result[List[Task]]:
        """Retrieve all tasks from the inbox"""
        tasks = self._api.get_tasks(filter="inbox")
        return success([self._convert_todoist_task(t) for t in tasks])

    @with_retries("update task")
    def update_task(self, task_id: str, update: TaskUpdate) -> Result[bool]:
        """Apply updates to a specific task"""
        if not update.has_changes():
            return success(True)  # No changes needed

        update_args = {}
        if update.content is not None:
            update_args["content"] = update.content
        if update.labels is not None:
            update_args["labels"] = update.labels
        if update.section_id is not None:
            update_args["section_id"] = update.section_id
        if update.due is not None:
            update_args["due_string"] = update.due.string if update.due.string else update.due.date

        self._api.update_task(task_id=task_id, **update_args)
        return success(True)

    def _convert_todoist_task(self, todoist_task: TodoistTask) -> Task:
        """Convert Todoist API task to domain Task"""
        due = None
        if todoist_task.due:
            due = Due(
                date=todoist_task.due.date,
                datetime=todoist_task.due.datetime,
                string=todoist_task.due.string
            )

        return Task(
            id=todoist_task.id,
            content=todoist_task.content,
            project_id=todoist_task.project_id,
            labels=todoist_task.labels,
            due=due,
            section_id=todoist_task.section_id
        )