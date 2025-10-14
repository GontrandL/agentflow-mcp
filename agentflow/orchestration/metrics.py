"""
Real-time metrics tracking for SmartOrchestrator

Provides comprehensive performance monitoring including task timing,
error tracking, retry counts, token usage, and model performance metrics.
"""

from enum import Enum
import time
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union, Any
import structlog
from datetime import datetime
from collections import defaultdict


class MetricType(Enum):
    """Standardized metric categories"""
    TASK_DURATION = "task_duration"
    SUBTASK_DURATION = "subtask_duration"
    ERROR_COUNT = "error_count"
    RETRY_COUNT = "retry_count"
    TOKEN_USAGE = "token_usage"
    MODEL_USAGE = "model_usage"
    COST = "cost"


@dataclass
class Metric:
    """Base class for tracking individual metrics"""
    name: str
    values: List[Union[int, float]] = field(default_factory=list)

    def add_value(self, value: Union[int, float]) -> None:
        """Add a new value to the metric"""
        if not isinstance(value, (int, float)):
            raise TypeError(f"Value must be int or float, got {type(value)}")
        self.values.append(value)

    def get_stats(self) -> Dict[str, float]:
        """Calculate basic statistics for the metric"""
        if not self.values:
            return {
                "count": 0,
                "sum": 0.0,
                "avg": 0.0,
                "min": 0.0,
                "max": 0.0
            }

        return {
            "count": len(self.values),
            "sum": float(sum(self.values)),
            "avg": float(sum(self.values) / len(self.values)),
            "min": float(min(self.values)),
            "max": float(max(self.values))
        }

    def reset(self) -> None:
        """Clear all recorded values"""
        self.values.clear()


class OrchestratorMetrics:
    """
    Real-time metrics tracking for SmartOrchestrator

    Tracks:
    - Task execution timing (start/end/duration)
    - Subtask performance metrics
    - Error counts by type
    - Retry attempts
    - Token usage per model
    - Model invocation statistics
    - Cost tracking

    Example:
        >>> metrics = OrchestratorMetrics()
        >>> metrics.start_task("task_1")
        >>> # ... do work ...
        >>> duration = metrics.end_task("task_1")
        >>> summary = metrics.get_metrics_summary()
    """

    def __init__(self, logger: Optional[structlog.BoundLogger] = None):
        """
        Initialize metrics tracker

        Args:
            logger: Optional structlog logger instance
        """
        self.logger = logger or structlog.get_logger(__name__)

        # Initialize metric collectors
        self.metrics: Dict[MetricType, Metric] = {
            MetricType.TASK_DURATION: Metric("task_duration"),
            MetricType.SUBTASK_DURATION: Metric("subtask_duration"),
            MetricType.ERROR_COUNT: Metric("error_count"),
            MetricType.RETRY_COUNT: Metric("retry_count"),
            MetricType.TOKEN_USAGE: Metric("token_usage"),
            MetricType.MODEL_USAGE: Metric("model_usage"),
            MetricType.COST: Metric("cost")
        }

        # Task-specific tracking
        self.active_tasks: Dict[str, float] = {}
        self.completed_tasks: Dict[str, Dict[str, Any]] = {}

        # Subtask metrics by task_id
        self.subtask_metrics: Dict[str, Dict[str, Union[int, float]]] = defaultdict(dict)

        # Model usage statistics
        self.model_usage: Dict[str, Dict[str, int]] = defaultdict(
            lambda: {"count": 0, "tokens": 0, "cost": 0.0}
        )

        # Error tracking by type
        self.error_types: Dict[str, int] = defaultdict(int)

        # Session metadata
        self.session_start = datetime.now()
        self.total_tasks = 0
        self.successful_tasks = 0
        self.failed_tasks = 0

    def start_task(self, task_id: str) -> None:
        """
        Record task start time

        Args:
            task_id: Unique identifier for the task
        """
        self._validate_metric(task_id)

        if task_id in self.active_tasks:
            self.logger.warning(
                "task_already_active",
                task_id=task_id,
                message="Task already started, overwriting start time"
            )

        self.active_tasks[task_id] = time.time()
        self.total_tasks += 1

        self.logger.info(
            "task_started",
            task_id=task_id,
            timestamp=datetime.now().isoformat()
        )

    def end_task(self, task_id: str, success: bool = True) -> float:
        """
        Record task completion and return duration

        Args:
            task_id: Task identifier
            success: Whether task completed successfully

        Returns:
            Duration in seconds
        """
        if task_id not in self.active_tasks:
            self.logger.warning(
                "task_not_found",
                task_id=task_id,
                message="Task not found in active tasks"
            )
            return 0.0

        # Calculate duration
        start_time = self.active_tasks.pop(task_id)
        duration = time.time() - start_time

        # Record metrics
        self.metrics[MetricType.TASK_DURATION].add_value(duration)

        # Track success/failure
        if success:
            self.successful_tasks += 1
        else:
            self.failed_tasks += 1

        # Store completion record
        self.completed_tasks[task_id] = {
            "duration": duration,
            "success": success,
            "completed_at": datetime.now().isoformat()
        }

        self.logger.info(
            "task_completed",
            task_id=task_id,
            duration=round(duration, 3),
            success=success,
            timestamp=datetime.now().isoformat()
        )

        return duration

    def record_error(self, task_id: str, error_type: str, error_message: str = "") -> None:
        """
        Increment error count for a specific error type

        Args:
            task_id: Task identifier
            error_type: Type/category of error
            error_message: Optional error message
        """
        self._validate_metric(task_id)
        self._validate_metric(error_type)

        # Increment counters
        self.metrics[MetricType.ERROR_COUNT].add_value(1)
        self.error_types[error_type] += 1

        # Track in subtask metrics
        error_key = f"error_{error_type}"
        self.subtask_metrics[task_id][error_key] = (
            self.subtask_metrics[task_id].get(error_key, 0) + 1
        )

        self.logger.error(
            "task_error",
            task_id=task_id,
            error_type=error_type,
            error_message=error_message,
            timestamp=datetime.now().isoformat()
        )

    def record_retry(self, task_id: str, attempt: int = 1) -> None:
        """
        Increment retry count for a task

        Args:
            task_id: Task identifier
            attempt: Current attempt number
        """
        self._validate_metric(task_id)

        self.metrics[MetricType.RETRY_COUNT].add_value(1)
        self.subtask_metrics[task_id]["retries"] = (
            self.subtask_metrics[task_id].get("retries", 0) + 1
        )

        self.logger.warning(
            "task_retry",
            task_id=task_id,
            attempt=attempt,
            timestamp=datetime.now().isoformat()
        )

    def record_token_usage(self, model_name: str, input_tokens: int,
                          output_tokens: int, cost: float = 0.0) -> None:
        """
        Record token usage for a specific model

        Args:
            model_name: Name/identifier of the model
            input_tokens: Number of input tokens used
            output_tokens: Number of output tokens generated
            cost: Cost in dollars
        """
        self._validate_metric(model_name)

        total_tokens = input_tokens + output_tokens

        # Record metrics
        self.metrics[MetricType.TOKEN_USAGE].add_value(total_tokens)
        self.metrics[MetricType.COST].add_value(cost)

        # Update model-specific tracking
        self.model_usage[model_name]["count"] += 1
        self.model_usage[model_name]["tokens"] += total_tokens
        self.model_usage[model_name]["cost"] += cost

        self.logger.info(
            "token_usage",
            model=model_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            cost=round(cost, 6),
            timestamp=datetime.now().isoformat()
        )

    def record_subtask_completion(self, task_id: str, subtask_id: str,
                                 duration: float, success: bool = True) -> None:
        """
        Record subtask completion with duration

        Args:
            task_id: Parent task identifier
            subtask_id: Subtask identifier
            duration: Execution duration in seconds
            success: Whether subtask completed successfully
        """
        self._validate_metric(task_id)
        self._validate_metric(subtask_id)

        self.metrics[MetricType.SUBTASK_DURATION].add_value(duration)

        # Store in subtask metrics
        self.subtask_metrics[task_id][f"subtask_{subtask_id}_duration"] = duration
        self.subtask_metrics[task_id][f"subtask_{subtask_id}_success"] = success

        self.logger.info(
            "subtask_completed",
            task_id=task_id,
            subtask_id=subtask_id,
            duration=round(duration, 3),
            success=success,
            timestamp=datetime.now().isoformat()
        )

    def record_model_usage(self, model_name: str) -> None:
        """
        Record model invocation count

        Args:
            model_name: Name/identifier of the model
        """
        self._validate_metric(model_name)

        self.metrics[MetricType.MODEL_USAGE].add_value(1)
        self.model_usage[model_name]["count"] += 1

        self.logger.debug(
            "model_invocation",
            model=model_name,
            timestamp=datetime.now().isoformat()
        )

    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics for all metrics

        Returns:
            Dictionary with aggregated metrics
        """
        summary = {
            "session_start": self.session_start.isoformat(),
            "session_duration": (datetime.now() - self.session_start).total_seconds(),
            "total_tasks": self.total_tasks,
            "successful_tasks": self.successful_tasks,
            "failed_tasks": self.failed_tasks,
            "success_rate": (
                self.successful_tasks / self.total_tasks
                if self.total_tasks > 0 else 0.0
            ),
            "active_tasks": len(self.active_tasks),
            "metrics": {
                metric_type.value: metric.get_stats()
                for metric_type, metric in self.metrics.items()
            },
            "model_usage": dict(self.model_usage),
            "error_types": dict(self.error_types),
            "total_cost": sum(self.metrics[MetricType.COST].values)
        }

        return summary

    def get_task_metrics(self, task_id: str) -> Dict[str, Union[int, float]]:
        """
        Get metrics for a specific task

        Args:
            task_id: Task identifier

        Returns:
            Dictionary of task-specific metrics
        """
        metrics = dict(self.subtask_metrics.get(task_id, {}))

        # Add completion data if available
        if task_id in self.completed_tasks:
            metrics.update(self.completed_tasks[task_id])

        return metrics

    def get_subtask_metrics(self) -> Dict[str, Dict[str, Union[int, float]]]:
        """
        Get all subtask metrics

        Returns:
            Dictionary mapping task_id to subtask metrics
        """
        return dict(self.subtask_metrics)

    def get_model_metrics(self) -> Dict[str, Dict[str, Union[int, float]]]:
        """
        Get model usage statistics

        Returns:
            Dictionary with per-model usage statistics
        """
        return dict(self.model_usage)

    def reset_metrics(self) -> None:
        """Reset all metrics to initial state"""
        for metric in self.metrics.values():
            metric.reset()

        self.active_tasks.clear()
        self.completed_tasks.clear()
        self.subtask_metrics.clear()
        self.model_usage.clear()
        self.error_types.clear()

        self.session_start = datetime.now()
        self.total_tasks = 0
        self.successful_tasks = 0
        self.failed_tasks = 0

        self.logger.info("metrics_reset", timestamp=datetime.now().isoformat())

    def save_to_disk(self, filepath: str) -> None:
        """
        Save current metrics to disk as JSON

        Args:
            filepath: Path to save metrics file
        """
        summary = self.get_metrics_summary()

        # Ensure directory exists
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)

        # Write JSON
        with open(filepath, 'w') as f:
            json.dump(summary, f, indent=2)

        self.logger.info(
            "metrics_saved",
            filepath=filepath,
            timestamp=datetime.now().isoformat()
        )

    def _validate_metric(self, identifier: str) -> None:
        """
        Validate metric identifier format

        Args:
            identifier: Metric identifier to validate

        Raises:
            ValueError: If identifier is invalid
        """
        if not isinstance(identifier, str) or not identifier.strip():
            raise ValueError(f"Invalid metric identifier: {identifier}")
