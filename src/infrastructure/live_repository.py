from typing import List, Optional
from todoist_api_python.api import TodoistAPI
from todoist_api_python.models import Task as TodoistTask
from todoist_api_python.models import Project as TodoistProject

from src.domain.repository import TodoistRepository
from src.domain.task import Task, Due
from src.domain.task_update import TaskUpdate
from src.domain.result import Result, success, error

class LiveTodoistRepository(TodoistRepository):
    """Live implementation of TodoistRepository using the Todoist API"""
    
    def __init__(self, api_token: str):
        self._api = TodoistAPI(api_token)

    def get_inbox_tasks(self) -> Result[List[Task]]:
        """Retrieve all tasks from the inbox"""
        try:
            tasks = self._api.get_tasks(filter="inbox")
            return success([self._convert_todoist_task(t) for t in tasks])
        except Exception as e:
            return error(f"Failed to fetch inbox tasks: {str(e)}")

    def update_task(self, task_id: str, update: TaskUpdate) -> Result[bool]:
        """Apply updates to a specific task"""
        if not update.has_changes():
            return success(True)  # No changes needed

        try:
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
        except Exception as e:
            return error(f"Failed to update task: {str(e)}")

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