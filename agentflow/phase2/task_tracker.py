# Subtask 1: Implement Task Dataclass
from dataclasses import dataclass, field
from typing import List

@dataclass
class Task:
    """Represents a task in a task management system.

    Attributes:
        id (str): A unique identifier for the task. Must be non-empty.
        difficulty (str): The difficulty level of the task. Must be one of 'low', 'medium', or 'high'.
        error_risk (str): The risk level of errors in the task. Must be one of 'low', 'medium', or 'high'.
        estimated_tokens (int): The estimated number of tokens required to complete the task. Must be non-negative.
        description (str): A detailed description of the task. Defaults to an empty string.
        dependencies (List[str]): A list of task IDs that this task depends on. Defaults to an empty list.
    """
    id: str
    difficulty: str
    error_risk: str
    estimated_tokens: int
    description: str = ""
    dependencies: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Validates the fields after the dataclass is initialized."""
        if not self.id:
            raise ValueError("Task ID cannot be empty.")
        if self.difficulty not in {"low", "medium", "high"}:
            raise ValueError("Difficulty must be 'low', 'medium', or 'high'.")
        if self.error_risk not in {"low", "medium", "high"}:
            raise ValueError("Error risk must be 'low', 'medium', or 'high'.")
        if self.estimated_tokens < 0:
            raise ValueError("Estimated tokens must be a non-negative integer.")

# Subtask 2: Implement TaskTracker Class Initialization and Directory Structure
import os
import json
from typing import List, Dict, Optional, Union
from pathlib import Path

class TaskTracker:
    """A class to track tasks with dependencies and manage related file structure."""

    VALID_STATUSES = {"pending", "in_progress", "completed", "failed"}

    def __init__(self, project_root: str, tasks: Optional[List[Dict]] = None) -> None:
        """Initialize TaskTracker with project root and optional tasks.
        
        Args:
            project_root: Root directory for project files
            tasks: List of task dictionaries (optional)
            
        Raises:
            ValueError: For invalid inputs or task data
            OSError: If directory creation fails
        """
        self._validate_project_root(project_root)
        self.project_root = Path(project_root)
        self.tasks: Dict[str, Dict] = {}
        
        self._setup_directory_structure()
        
        if tasks:
            for task in tasks:
                self.add_task(task)

    def _validate_project_root(self, path: str) -> None:
        """Validate the project root path string.
        
        Args:
            path: Path to validate
            
        Raises:
            ValueError: If path is invalid
        """
        try:
            Path(path)
        except (TypeError, ValueError) as e:
            raise ValueError(f"Invalid project_root path: {e}")

    def _setup_directory_structure(self) -> None:
        """Create required directory structure.
        
        Raises:
            OSError: If directory creation fails
        """
        try:
            self.project_root.mkdir(exist_ok=True)
            (self.project_root / "tasks").mkdir(exist_ok=True)
            (self.project_root / "logs").mkdir(exist_ok=True)
            (self.project_root / "outputs").mkdir(exist_ok=True)
        except OSError as e:
            raise OSError(f"Failed to create directory structure: {e}")

    def _validate_task(self, task: Dict) -> None:
        """Validate a task dictionary.
        
        Args:
            task: Task dictionary to validate
            
        Raises:
            ValueError: For invalid task data
        """
        if "id" not in task:
            raise ValueError("Task missing required field: id")
            
        if task["id"] in self.tasks:
            raise ValueError(f"Duplicate task id: {task['id']}")
            
        if "description" not in task:
            raise ValueError("Task missing required field: description")
            
        if "status" not in task or task["status"] not in self.VALID_STATUSES:
            raise ValueError(f"Invalid status. Must be one of: {self.VALID_STATUSES}")
            
        if "dependencies" not in task or not isinstance(task["dependencies"], list):
            raise ValueError("Task must have 'dependencies' list (can be empty)")
            
        for dep_id in task["dependencies"]:
            if dep_id not in self.tasks:
                raise ValueError(f"Dependency ID not found: {dep_id}")

    def _save_task_to_file(self, task_id: str) -> None:
        """Save task data to JSON file.
        
        Args:
            task_id: ID of task to save
            
        Raises:
            OSError: If file operation fails
        """
        try:
            task_file = self.project_root / "tasks" / f"{task_id}.json"
            with open(task_file, "w", encoding="utf-8") as f:
                json.dump(self.tasks[task_id], f, indent=2)
        except OSError as e:
            raise OSError(f"Failed to save task {task_id}: {e}")

    def add_task(self, task: Dict) -> None:
        """Add a new task after validation.
        
        Args:
            task: Task dictionary to add
            
        Raises:
            ValueError: For invalid task data
            OSError: If file operation fails
        """
        self._validate_task(task)
        self.tasks[task["id"]] = task
        self._save_task_to_file(task["id"])

    def get_task(self, task_id: str) -> Dict:
        """Retrieve a task by ID.
        
        Args:
            task_id: ID of task to retrieve
            
        Returns:
            The requested task dictionary
            
        Raises:
            KeyError: If task ID not found
        """
        if task_id not in self.tasks:
            raise KeyError(f"Task not found: {task_id}")
        return self.tasks[task_id]

    def update_status(self, task_id: str, new_status: str) -> None:
        """Update a task's status.
        
        Args:
            task_id: ID of task to update
            new_status: New status value
            
        Raises:
            KeyError: If task ID not found
            ValueError: If new status is invalid
            OSError: If file operation fails
        """
        if task_id not in self.tasks:
            raise KeyError(f"Task not found: {task_id}")
            
        if new_status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid status. Must be one of: {self.VALID_STATUSES}")
            
        self.tasks[task_id]["status"] = new_status
        self._save_task_to_file(task_id)

# Subtask 3: Implement TaskTracker Methods
class TaskTracker:
    def __init__(self):
        self.tasks = []

    def add_task(self, task_id, task_name):
        # Check if task_id already exists
        if any(task['id'] == task_id for task in self.tasks):
            raise ValueError("Task ID already exists")
        
        # Check if task_name is valid
        if not isinstance(task_name, str) or not task_name.strip():
            raise TypeError("Invalid task name")
        
        # Add the new task with default status "pending"
        self.tasks.append({'id': task_id, 'name': task_name, 'status': 'pending'})

    def update_task_status(self, task_id, new_status):
        # Check if new_status is valid
        if new_status not in ['pending', 'in_progress', 'completed']:
            raise ValueError("Invalid status")
        
        # Find the task by task_id
        task = next((task for task in self.tasks if task['id'] == task_id), None)
        
        # Check if task_id exists
        if task is None:
            raise ValueError("Task ID not found")
        
        # Update the task status
        task['status'] = new_status

    def get_active_tasks(self):
        # Return all tasks that are not completed
        return [task for task in self.tasks if task['status'] != 'completed']
