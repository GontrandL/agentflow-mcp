import logging
from typing import Optional, Dict, Set, List, Union, Any, Callable

class EscalationEngine:
    """A class to handle task escalations based on predefined rules.

    Attributes:
        tasks (Dict[str, Dict]): A dictionary to store tasks with their details.
        escalated_tasks (Set[str]): A set to keep track of escalated tasks.
    """

    def __init__(self):
        """Initializes the EscalationEngine with empty tasks and escalated_tasks."""
        self.tasks: Dict[str, Dict] = {}
        self.escalated_tasks: Set[str] = set()
        logging.basicConfig(level=logging.INFO)

    def should_escalate(self, result: dict, current_tier: int) -> bool:
        """
        Determines if the given result should escalate to a higher tier.

        Args:
            result (dict): A dictionary containing at least the keys 'severity' (int) and 'confidence' (float).
            current_tier (int): The current escalation tier.

        Returns:
            bool: True if the result should escalate, False otherwise.
        """
        # Check for invalid inputs
        if not isinstance(result, dict) or 'severity' not in result or 'confidence' not in result:
            return False

        try:
            severity = int(result['severity'])
            confidence = float(result['confidence'])
        except (ValueError, TypeError):
            return False

        # Validate ranges
        if not (0 <= severity <= 10) or not (0.0 <= confidence <= 1.0):
            return False

        if not (0 <= current_tier <= 5):
            return False

        # Denial rules (checked first)
        if severity < 3:
            return False
        if current_tier >= 5:
            return False

        # Severity-based escalation
        if severity >= 8 and confidence >= 0.8:
            return True

        # Confidence-based escalation
        if confidence < 0.5 and severity >= 5 and current_tier < 2:
            return True

        # Tier-based escalation
        if current_tier < 3 and severity >= 6:
            return True

        # If none of the escalation conditions are met
        return False

    def _free_tier_failed(self, result) -> bool:
        """Checks if the free tier failed based on attempts or quality.

        Args:
            result (dict): A dictionary containing 'attempts' and 'quality' keys.

        Returns:
            bool: True if the free tier failed, False otherwise.
        """
        if result is None:
            return True
        attempts = result.get("attempts", 0)
        quality = result.get("quality", 0)
        if not isinstance(attempts, int) or not isinstance(quality, int):
            return True
        if attempts < 0 or quality < 0:
            return True
        return attempts >= 3 or quality < 6

    def _mid_tier_failed(self, result) -> bool:
        """Checks if the mid tier failed based on attempts or quality.

        Args:
            result (dict): A dictionary containing 'attempts' and 'quality' keys.

        Returns:
            bool: True if the mid tier failed, False otherwise.
        """
        if result is None:
            return True

        # Default values for quality and attempts
        quality = result.get('quality', 10)
        attempts = result.get('attempts', 0)

        # Handle invalid values by setting defaults
        try:
            quality = int(quality)
        except (ValueError, TypeError):
            quality = 10

        try:
            attempts = int(attempts)
        except (ValueError, TypeError):
            attempts = 0

        # Check the failure conditions
        return quality < 8 or attempts >= 2

    def get_next_tier(self, current_tier: str | None) -> str:
        """Determines the next escalation tier.

        Args:
            current_tier (str | None): The current escalation tier.

        Returns:
            str: The next escalation tier.

        Raises:
            TypeError: If the current_tier is not a string or None.
        """
        # Validate input type
        if not (current_tier is None or isinstance(current_tier, str)):
            raise TypeError("Input must be a string or None")

        # Normalize input to lowercase and handle None or empty string
        if current_tier is None or current_tier.strip() == "":
            return 'free'

        current_tier = current_tier.lower()

        # Define the tier escalation order
        tiers = ['free', 'mid', 'premium', 'premium', 'premium']

        # Find the index of the current tier
        try:
            index = tiers.index(current_tier)
        except ValueError:
            # If current_tier is not in the list, default to 'free'
            return 'free'

        # Determine the next tier
        if index < len(tiers) - 1:
            return tiers[index + 1]
        else:
            return tiers[index]  # 'premium' remains 'premium'

    def escalate_task(self, task_id: str) -> bool:
        """
        Escalates a task based on its ID.

        Args:
            task_id (str): The ID of the task to escalate.

        Returns:
            bool: True if the task was successfully escalated, False otherwise.

        Raises:
            ValueError: If the task ID is invalid or the task has already been escalated.
        """
        if not self.validate_task(task_id):
            logging.warning("Invalid task ID provided: %s", task_id)
            raise ValueError(f"Invalid task ID: {task_id}")

        if task_id in self.escalated_tasks:
            logging.warning("Task already escalated: %s", task_id)
            raise ValueError(f"Task already escalated: {task_id}")

        task = self.tasks[task_id]
        if not task.get('dependencies', []):
            logging.warning("Missing dependencies for task: %s", task_id)
            raise ValueError(f"Missing dependencies for task: {task_id}")

        self.escalated_tasks.add(task_id)
        logging.info("Task escalated successfully: %s", task_id)
        return True

    def validate_task(self, task_id: str) -> bool:
        """
        Validates a task based on its ID.

        Args:
            task_id (str): The ID of the task to validate.

        Returns:
            bool: True if the task is valid, False otherwise.
        """
        if not task_id:
            logging.warning("Empty task ID provided.")
            return False

        if task_id not in self.tasks:
            logging.warning("Task ID not found: %s", task_id)
            return False

        return True

# Example usage:
# engine = EscalationEngine()
# engine.tasks = {
#     'task1': {'dependencies': ['dep1', 'dep2']},
#     'task2': {'dependencies': []}
# }
# engine.escalate_task('task1')  # Should escalate successfully
# engine.escalate_task('task2')  # Should raise ValueError due to missing dependencies
# engine.escalate_task('task3')  # Should raise ValueError due to invalid task ID