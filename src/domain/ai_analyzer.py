from abc import ABC, abstractmethod
from typing import List
from src.domain.task import Task
from src.domain.project import Project
from src.domain.result import Result
from src.domain.task_suggestion import TaskSuggestion

class AITaskAnalyzer(ABC):
    """Interface for AI-powered task analysis"""
    
    @abstractmethod
    def analyze_tasks(self, tasks: List[Task], projects: List[Project]) -> Result[List[TaskSuggestion]]:
        """
        Analyze a list of tasks and suggest appropriate projects and metadata
        
        Args:
            tasks: List of tasks to analyze
            projects: List of available projects for suggestions
            
        Returns:
            Result containing list of TaskSuggestion objects or error
        """
        pass