"""
KnowledgeBase Module - Core Phase 2 Component

Manages patterns and insights with file persistence.
Simplified version without ML dependencies for basic Phase 2 functionality.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict, Any
import json
import os

# Data Classes
@dataclass
class Pattern:
    """Represents a design pattern.

    Attributes:
        id (int): Unique identifier for the pattern.
        name (str): Name of the pattern.
        description (str, optional): Detailed description of the pattern. Defaults to None.
        category (str, optional): Category of the pattern. Defaults to None.
        complexity (int): Complexity level from 1-10. Defaults to 1.
        tags (List[str], optional): List of tags associated with the pattern. Defaults to None.
        is_active (bool): Indicates if the pattern is active. Defaults to True.
    """
    id: int
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    complexity: int = 1
    tags: Optional[List[str]] = None
    is_active: bool = True

    def __post_init__(self):
        if self.complexity < 1 or self.complexity > 10:
            raise ValueError("Complexity must be between 1 and 10.")
        if self.tags is None:
            self.tags = []

@dataclass
class ProjectInsight:
    """Represents insights into a project's use of design patterns.

    Attributes:
        project_id (int): Unique identifier for the project.
        patterns_used (List[Pattern]): List of patterns used in the project.
        success_rate (float): Success rate of the project from 0.0 to 1.0. Defaults to 0.0.
        feedback (str, optional): Feedback on the project. Defaults to None.
        created_at (datetime): Timestamp when the insight was created. Defaults to current time.
    """
    project_id: int
    patterns_used: List[Pattern]
    success_rate: float = 0.0
    feedback: Optional[str] = None
    created_at: datetime = None

    def __post_init__(self):
        if self.success_rate < 0.0 or self.success_rate > 1.0:
            raise ValueError("Success rate must be between 0.0 and 1.0.")
        if self.feedback is None:
            self.feedback = ""
        if self.created_at is None:
            self.created_at = datetime.now()

# Knowledge Base Class
class KnowledgeBase:
    """A class to manage a collection of patterns and insights with file persistence."""

    def __init__(self) -> None:
        """Initialize an empty knowledge base."""
        self._patterns: List[str] = []
        self._insights: List[str] = []

    @property
    def patterns(self) -> List[str]:
        """Get the list of patterns."""
        return self._patterns.copy()

    @property
    def insights(self) -> List[str]:
        """Get the list of insights."""
        return self._insights.copy()

    def add_pattern(self, pattern: str) -> None:
        """
        Add a pattern to the knowledge base if it doesn't already exist.

        Args:
            pattern: The pattern to add.
        """
        if pattern not in self._patterns:
            self._patterns.append(pattern)

    def add_insight(self, insight: str) -> None:
        """
        Add an insight to the knowledge base if it doesn't already exist.

        Args:
            insight: The insight to add.
        """
        if insight not in self._insights:
            self._insights.append(insight)

    def save(self, file_path: str) -> None:
        """
        Save the knowledge base to a JSON file.

        Args:
            file_path: Path to the file where the knowledge base will be saved.

        Raises:
            ValueError: If the file path is invalid or not writable.
            IOError: If there's an error during file writing.
        """
        if not file_path:
            raise ValueError("File path cannot be empty.")

        try:
            data = {
                "patterns": self._patterns,
                "insights": self._insights
            }
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
        except (IOError, OSError) as e:
            raise IOError(f"Failed to save knowledge base to {file_path}: {str(e)}")
        except TypeError as e:
            raise IOError(f"Failed to serialize knowledge base: {str(e)}")

    def load(self, file_path: str) -> None:
        """
        Load the knowledge base from a JSON file.

        Args:
            file_path: Path to the file from which to load the knowledge base.

        Raises:
            ValueError: If the file path is invalid or the file doesn't exist.
            IOError: If the file is corrupted or cannot be read.
        """
        if not file_path or not os.path.exists(file_path):
            raise ValueError(f"File not found: {file_path}")

        try:
            with open(file_path, 'r') as f:
                data: Dict[str, Any] = json.load(f)
        except (IOError, OSError) as e:
            raise IOError(f"Failed to read file {file_path}: {str(e)}")
        except json.JSONDecodeError as e:
            raise IOError(f"Corrupted or invalid JSON file {file_path}: {str(e)}")

        # Validate loaded data structure
        if not isinstance(data, dict):
            raise IOError(f"Invalid data format in {file_path}: expected dictionary")

        # Process patterns if they exist in the file
        if "patterns" in data:
            if not isinstance(data["patterns"], list):
                raise IOError(f"Invalid patterns format in {file_path}: expected list")
            self._patterns = []
            for pattern in data["patterns"]:
                self.add_pattern(str(pattern))

        # Process insights if they exist in the file
        if "insights" in data:
            if not isinstance(data["insights"], list):
                raise IOError(f"Invalid insights format in {file_path}: expected list")
            self._insights = []
            for insight in data["insights"]:
                self.add_insight(str(insight))

    def __eq__(self, other: object) -> bool:
        """Compare two KnowledgeBase instances for equality."""
        if not isinstance(other, KnowledgeBase):
            return False
        return self._patterns == other._patterns and self._insights == other._insights

    def __repr__(self) -> str:
        """Return a string representation of the KnowledgeBase."""
        return f"KnowledgeBase(patterns={len(self._patterns)}, insights={len(self._insights)})"


# Task Recommendation Function (simplified version without ML)
def get_recommendations_for_task(task: Dict, workers: List[Dict]) -> List[Dict]:
    """
    Matches tasks to available workers based on smart criteria and tracks confidence scores.

    Args:
        task (dict): Contains keys 'id', 'description', 'requirements' (list of skills), 'priority' (int 1-5).
        workers (list of dicts): Each worker has 'id', 'skills' (list), 'current_load' (int), 'reliability' (float 0-1).

    Returns:
        list: A list of dictionaries containing worker_id, confidence score, and match reason, sorted by confidence (descending).
    """
    recommendations = []

    # Handle missing requirements in the task
    task_requirements = task.get('requirements', [])
    task_priority = task.get('priority', 1)

    for worker in workers:
        worker_skills = worker.get('skills', [])
        worker_load = worker.get('current_load', 0)
        worker_reliability = worker.get('reliability', 0.5)

        # Skill Match Criteria
        if task_requirements:
            common_skills = set(worker_skills).intersection(task_requirements)
            skill_match_ratio = len(common_skills) / len(task_requirements)
        else:
            skill_match_ratio = 1.0

        # Load Check Criteria
        if worker_load >= 3:
            continue

        # Priority Handling
        if task_priority >= 4 and worker_reliability < 0.8:
            continue

        # Confidence Score Calculation
        confidence = (skill_match_ratio * 0.6) + (worker_reliability * 0.3) + (1 - worker_load / 5 * 0.1)
        confidence = round(confidence, 2)

        # Match Reason
        match_reason = []
        if skill_match_ratio >= 0.6:
            match_reason.append("high skill match" if skill_match_ratio >= 0.8 else "partial skill match")
        else:
            match_reason.append("low skill match")
        if worker_reliability >= 0.8:
            match_reason.append("high reliability")
        if worker_load <= 1:
            match_reason.append("low load")
        elif worker_load == 2:
            match_reason.append("moderate load")

        match_reason_str = " + ".join(match_reason)

        recommendations.append({
            "worker_id": worker['id'],
            "confidence": confidence,
            "match_reason": match_reason_str
        })

    # Sort by confidence (descending), then by worker reliability
    recommendations.sort(key=lambda x: (-x['confidence'], -next((w['reliability'] for w in workers if w['id'] == x['worker_id']), 0)))

    return recommendations
