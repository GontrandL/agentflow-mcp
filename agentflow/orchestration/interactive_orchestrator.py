import logging
import time
from typing import List, Dict, Any, Set, Optional
from collections import defaultdict
from enum import Enum, auto

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TaskStatus(Enum):
    PENDING = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    FAILED = auto()

class InvalidTaskError(Exception):
    """Raised when a task is invalid (missing required fields)."""
    pass

class TaskNotFoundError(Exception):
    """Raised when a task is not found in the orchestrator."""
    pass

class CircularDependencyError(Exception):
    """Raised when tasks have circular dependencies."""
    pass

class InteractiveOrchestrator:
    """Orchestrator for managing and executing tasks in an interactive environment."""

    def __init__(self):
        """Initialize the orchestrator with task storage and logging."""
        self.tasks: Dict[str, dict] = {}  # Stores task details by ID
        self.task_status: Dict[str, TaskStatus] = {}  # Tracks task status
        self.task_dependencies: Dict[str, Set[str]] = defaultdict(set)  # Tracks dependencies
        self.task_dependents: Dict[str, Set[str]] = defaultdict(set)  # Reverse dependencies
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(handler)

    def add_task(self, task: dict) -> None:
        """
        Add a task to the orchestrator after validation.

        Args:
            task: Dictionary containing task details with keys:
                - id: Unique identifier for the task
                - description: Description of the task
                - dependencies: List of task IDs this task depends on

        Raises:
            InvalidTaskError: If the task is missing required fields or has invalid data.
        """
        required_fields = {'id', 'description', 'dependencies'}
        if not all(field in task for field in required_fields):
            raise InvalidTaskError(f"Task must contain all fields: {required_fields}")

        task_id = task['id']
        if task_id in self.tasks:
            self.logger.warning(f"Task with ID '{task_id}' already exists. Overwriting.")

        self.tasks[task_id] = task
        self.task_status[task_id] = TaskStatus.PENDING

        # Clear existing dependencies
        if task_id in self.task_dependencies:
            for dep in self.task_dependencies[task_id]:
                self.task_dependents[dep].discard(task_id)
        self.task_dependencies[task_id] = set()

        # Add new dependencies
        for dep in task['dependencies']:
            self.task_dependencies[task_id].add(dep)
            self.task_dependents[dep].add(task_id)

    def _check_circular_dependencies(self) -> None:
        """Check for circular dependencies in the task graph."""
        visited = set()
        recursion_stack = set()

        def visit(task_id):
            if task_id in recursion_stack:
                raise CircularDependencyError(f"Circular dependency detected involving task '{task_id}'")
            if task_id not in visited:
                recursion_stack.add(task_id)
                for dep in self.task_dependencies[task_id]:
                    visit(dep)
                recursion_stack.remove(task_id)
                visited.add(task_id)

        for task_id in self.tasks:
            if task_id not in visited:
                visit(task_id)

    def _get_ready_tasks(self) -> List[str]:
        """Return a list of task IDs that have all dependencies met."""
        ready_tasks = []
        for task_id in self.tasks:
            if self.task_status[task_id] == TaskStatus.PENDING:
                deps_met = all(
                    self.task_status[dep] == TaskStatus.COMPLETED
                    for dep in self.task_dependencies[task_id]
                )
                if deps_met:
                    ready_tasks.append(task_id)
        return ready_tasks

    def execute_tasks(self) -> None:
        """
        Execute all tasks in dependency order.

        Handles task failures gracefully and logs outcomes. Skips tasks whose
        dependencies are not met or have failed.
        """
        if not self.tasks:
            self.logger.info("No tasks to execute.")
            return

        try:
            self._check_circular_dependencies()
        except CircularDependencyError as e:
            self.logger.error(f"Execution aborted: {str(e)}")
            return

        while True:
            ready_tasks = self._get_ready_tasks()
            if not ready_tasks:
                break

            for task_id in ready_tasks:
                task = self.tasks[task_id]
                self.task_status[task_id] = TaskStatus.IN_PROGRESS
                self.logger.info(f"Executing task '{task_id}': {task['description']}")

                try:
                    # In a real implementation, this would call the actual task execution logic
                    # For this example, we'll simulate execution with a simple pass
                    # Replace with actual task execution logic as needed
                    self._execute_task(task)
                    self.task_status[task_id] = TaskStatus.COMPLETED
                    self.logger.info(f"Task '{task_id}' completed successfully")
                except Exception as e:
                    self.task_status[task_id] = TaskStatus.FAILED
                    self.logger.error(f"Task '{task_id}' failed: {str(e)}")

        # Check for pending tasks that couldn't run due to failed dependencies
        pending_tasks = [
            task_id for task_id, status in self.task_status.items()
            if status == TaskStatus.PENDING
        ]
        if pending_tasks:
            self.logger.warning(
                f"{len(pending_tasks)} tasks could not be executed due to unmet dependencies: "
                f"{pending_tasks}"
            )

    def _execute_task(self, task: dict) -> None:
        """Simulate task execution. Replace with actual task execution logic."""
        pass  # In a real implementation, this would execute the task

    def get_task_status(self, task_id: str) -> TaskStatus:
        """
        Get the status of a task.

        Args:
            task_id: ID of the task to check.

        Returns:
            The current status of the task.

        Raises:
            TaskNotFoundError: If the task ID is not found.
        """
        if task_id not in self.task_status:
            raise TaskNotFoundError(f"Task '{task_id}' not found")
        return self.task_status[task_id]

# Example usage
if __name__ == "__main__":
    tasks = [{"id": "task_1", "action": "process_data", "params": {"data": [1, 2, 3]}}]
    config = {"timeout": 5, "log_level": "DEBUG"}
    orchestrator = InteractiveOrchestrator()
    result = orchestrator.orchestrate(tasks, config)
    print(result)