from typing import List, Dict, Optional
from src.domain.ai_analyzer import AITaskAnalyzer
from src.domain.task import Task
from src.domain.project import Project
from src.domain.result import Result, success, error
from src.domain.task_suggestion import TaskSuggestion

class MockAIAnalyzer(AITaskAnalyzer):
    """Mock implementation of AITaskAnalyzer for testing"""
    
    def __init__(self, should_fail: bool = False):
        self.should_fail = should_fail
        # Predefined patterns for task classification
        self.patterns: Dict[str, Dict] = {
            "work": {
                "keywords": ["meeting", "presentation", "report", "client"],
                "project_id": "work",
                "confidence": 0.9,
                "labels": ["work"]
            },
            "personal": {
                "keywords": ["gym", "shopping", "call mom", "doctor"],
                "project_id": "personal",
                "confidence": 0.85,
                "labels": ["personal"]
            },
            "shopping": {
                "keywords": ["buy", "purchase", "get", "order"],
                "project_id": "shopping",
                "confidence": 0.8,
                "labels": ["shopping"]
            }
        }

    def analyze_tasks(self, tasks: List[Task], projects: List[Project]) -> Result[List[TaskSuggestion]]:
        """Analyze tasks based on predefined patterns"""
        if self.should_fail:
            return error("AI analysis failed")
            
        if not tasks:
            return success([])
            
        if not projects:
            return error("No projects available for classification")

        suggestions: List[TaskSuggestion] = []
        project_map = {p.id: p for p in projects}

        for task in tasks:
            suggestion = self._analyze_single_task(task, project_map)
            if suggestion:
                suggestions.append(suggestion)

        return success(suggestions)

    def _analyze_single_task(self, task: Task, project_map: Dict[str, Project]) -> Optional[TaskSuggestion]:
        """Analyze a single task using predefined patterns"""
        best_match = None
        highest_confidence = 0.0

        for pattern_name, pattern in self.patterns.items():
            if any(keyword in task.content.lower() for keyword in pattern["keywords"]):
                project_id = pattern["project_id"]
                if project_id in project_map:
                    confidence = pattern["confidence"]
                    if confidence > highest_confidence:
                        highest_confidence = confidence
                        best_match = pattern

        if best_match:
            return TaskSuggestion(
                task_id=task.id,
                suggested_project_id=best_match["project_id"],
                confidence=best_match["confidence"],
                explanation=f"Task matches {len(best_match['keywords'])} keywords for {best_match['project_id']} project",
                suggested_labels=best_match["labels"]
            )

        # Default suggestion with low confidence if no pattern matches
        return TaskSuggestion(
            task_id=task.id,
            suggested_project_id="inbox",
            confidence=0.3,
            explanation="No clear pattern matches found",
            suggested_labels=[]
        )
