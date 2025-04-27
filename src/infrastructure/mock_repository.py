from typing import List, Dict, Optional
from src.domain.repository import TodoistRepository
from src.domain.task import Task, Due
from src.domain.task_update import TaskUpdate
from src.domain.result import Result, success, error

class MockTodoistRepository(TodoistRepository):
    def __init__(self, should_fail: bool = False):
        self.should_fail = should_fail
        self.tasks: Dict[str, Task] = {
            "task1": Task(
                id="task1",
                content="Test task 1",
                project_id="inbox",
                labels=["test"],
                due=Due(date="2024-01-20")
            ),
            "task2": Task(
                id="task2",
                content="Test task 2",
                project_id="inbox"
            )
        }
        self.update_history: List[tuple[str, TaskUpdate]] = []

    def get_inbox_tasks(self) -> Result[List[Task]]:
        if self.should_fail:
            return error("Failed to fetch inbox tasks")
        return success([task for task in self.tasks.values()])

    def update_task(self, task_id: str, update: TaskUpdate) -> Result[bool]:
        if self.should_fail:
            return error("Failed to update task")
            
        if task_id not in self.tasks:
            return error(f"Task {task_id} not found")
            
        self.update_history.append((task_id, update))
        return success(True)