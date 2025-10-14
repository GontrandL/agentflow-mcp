"""
SmartOrchestrator with Enhanced Logging & Metrics

This module extends SmartOrchestrator with structured logging and real-time metrics tracking.
Import this instead of smart_orchestrator to get the enhanced version.
"""

import os
import time
from typing import Dict, Any, List, Optional
from functools import wraps

# Import base orchestrator
from .smart_orchestrator import SmartOrchestrator, Plan, Subtask, ValidationResult

# Import logging and metrics
from .logging_config import get_logger, setup_structlog
from .metrics import OrchestratorMetrics


def with_logging(method_name: str):
    """
    Decorator to add structured logging to orchestrator methods

    Args:
        method_name: Name of the method being logged
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            task_id = f"{method_name}_{int(time.time() * 1000)}"

            # Start tracking
            if hasattr(self, 'metrics') and self.metrics:
                self.metrics.start_task(task_id)

            if hasattr(self, 'structured_logger'):
                self.structured_logger.info(
                    f"{method_name}_started",
                    task_id=task_id,
                    method=method_name
                )

            try:
                # Execute method
                result = func(self, *args, **kwargs)

                # End tracking (success)
                if hasattr(self, 'metrics') and self.metrics:
                    duration = self.metrics.end_task(task_id, success=True)

                if hasattr(self, 'structured_logger'):
                    self.structured_logger.info(
                        f"{method_name}_completed",
                        task_id=task_id,
                        method=method_name,
                        duration=round(duration, 3) if hasattr(self, 'metrics') else None
                    )

                return result

            except Exception as e:
                # End tracking (failure)
                if hasattr(self, 'metrics') and self.metrics:
                    duration = self.metrics.end_task(task_id, success=False)
                    self.metrics.record_error(
                        task_id,
                        type(e).__name__,
                        str(e)
                    )

                if hasattr(self, 'structured_logger'):
                    self.structured_logger.error(
                        f"{method_name}_failed",
                        task_id=task_id,
                        method=method_name,
                        error_type=type(e).__name__,
                        error_message=str(e),
                        duration=round(duration, 3) if hasattr(self, 'metrics') else None
                    )

                raise

        return wrapper
    return decorator


class SmartOrchestratorWithLogging(SmartOrchestrator):
    """
    Enhanced SmartOrchestrator with structured logging and metrics tracking

    All methods are automatically instrumented with:
    - Structured JSON logging
    - Performance metrics
    - Error tracking
    - Cost monitoring

    Example:
        >>> setup_structlog(log_level='INFO', log_file='logs/orchestrator.log')
        >>> orchestrator = SmartOrchestratorWithLogging(provider='anthropic')
        >>> plan = orchestrator.analyze_and_plan(task, capabilities, context)
        >>> metrics = orchestrator.get_orchestrator_metrics()
    """

    def __init__(self, provider: str = 'anthropic', model: Optional[str] = None,
                 api_key: Optional[str] = None, enable_fallback: bool = True,
                 enable_metrics: bool = True, log_level: str = 'INFO',
                 log_file: Optional[str] = None):
        """
        Initialize SmartOrchestrator with logging and metrics

        Args:
            provider: Primary provider to use
            model: Specific model (or use provider default)
            api_key: API key (or read from env)
            enable_fallback: Enable automatic fallback chain on errors
            enable_metrics: Enable metrics tracking (default: True)
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
            log_file: Optional log file path
        """
        # Setup structured logging first
        setup_structlog(
            log_level=log_level,
            log_file=log_file or 'logs/orchestrator.log',
            enable_console=True
        )
        self.structured_logger = get_logger(__name__)

        # Initialize metrics
        self.metrics = None
        if enable_metrics:
            self.metrics = OrchestratorMetrics(logger=self.structured_logger)

        # Initialize parent orchestrator
        super().__init__(
            provider=provider,
            model=model,
            api_key=api_key,
            enable_fallback=enable_fallback
        )

        self.structured_logger.info(
            "orchestrator_initialized",
            provider=provider,
            model=self.model,
            enable_fallback=enable_fallback,
            enable_metrics=enable_metrics
        )

    @with_logging("analyze_and_plan")
    def analyze_and_plan(self, task: str, capabilities: List[str],
                         context: Dict[str, Any]) -> Plan:
        """
        Analyze task and generate optimal execution plan (with logging)

        Returns:
            Plan with subtasks, dependencies, requirements
        """
        self.structured_logger.info(
            "analyze_and_plan_details",
            task_length=len(task),
            num_capabilities=len(capabilities),
            context_keys=list(context.keys())
        )

        result = super().analyze_and_plan(task, capabilities, context)

        self.structured_logger.info(
            "plan_generated",
            complexity=result.complexity,
            decompose=result.decompose,
            num_subtasks=len(result.subtasks)
        )

        # Track model usage if metrics enabled
        if self.metrics:
            self.metrics.record_model_usage(self.model)
            cost = self.get_cost()
            self.metrics.record_token_usage(
                self.model,
                self.input_tokens,
                self.output_tokens,
                cost
            )

        return result

    @with_logging("assign_workers")
    def assign_workers(self, subtasks: List[Subtask],
                      available_workers: Dict[str, Dict]) -> Dict[str, str]:
        """
        Assign optimal worker for each subtask (with logging)

        Returns:
            Dict mapping subtask_id -> worker_name
        """
        self.structured_logger.info(
            "assign_workers_details",
            num_subtasks=len(subtasks),
            num_workers=len(available_workers),
            worker_names=list(available_workers.keys())
        )

        result = super().assign_workers(subtasks, available_workers)

        self.structured_logger.info(
            "workers_assigned",
            assignments=result
        )

        # Track model usage
        if self.metrics:
            self.metrics.record_model_usage(self.model)
            cost = self.get_cost()
            self.metrics.record_token_usage(
                self.model,
                self.input_tokens,
                self.output_tokens,
                cost
            )

        return result

    @with_logging("generate_specs")
    def generate_specs(self, subtask: Subtask, worker_info: Dict[str, Any],
                      full_context: Dict[str, Any] = None) -> str:
        """
        Generate ultra-detailed specs optimized for specific worker (with logging)

        Returns:
            Optimized prompt for worker
        """
        self.structured_logger.info(
            "generate_specs_details",
            subtask_id=subtask.id,
            worker_model=worker_info.get('model', 'unknown'),
            has_context=full_context is not None
        )

        result = super().generate_specs(subtask, worker_info, full_context)

        self.structured_logger.info(
            "specs_generated",
            subtask_id=subtask.id,
            spec_length=len(result)
        )

        # Track model usage
        if self.metrics:
            self.metrics.record_model_usage(self.model)
            cost = self.get_cost()
            self.metrics.record_token_usage(
                self.model,
                self.input_tokens,
                self.output_tokens,
                cost
            )

        return result

    @with_logging("validate_outputs")
    def validate_outputs(self, results: Dict[str, str],
                        requirements: Dict[str, Any]) -> ValidationResult:
        """
        Validate worker outputs against requirements (with logging)

        Returns:
            ValidationResult with scores and feedback
        """
        self.structured_logger.info(
            "validate_outputs_details",
            num_results=len(results),
            result_ids=list(results.keys())
        )

        result = super().validate_outputs(results, requirements)

        self.structured_logger.info(
            "validation_completed",
            all_passed=result.all_passed,
            avg_score=result.avg_score,
            num_failed=len(result.failed_tasks)
        )

        # Track model usage
        if self.metrics:
            self.metrics.record_model_usage(self.model)
            cost = self.get_cost()
            self.metrics.record_token_usage(
                self.model,
                self.input_tokens,
                self.output_tokens,
                cost
            )

            # Record validation metrics
            for task_result in result.results:
                self.metrics.record_subtask_completion(
                    "validation",
                    task_result['subtask_id'],
                    0.0,  # Duration not tracked at this level
                    task_result['passed']
                )

        return result

    @with_logging("assemble_and_polish")
    def assemble_and_polish(self, results: Dict[str, str],
                           plan: Plan) -> str:
        """
        Assemble multiple outputs into cohesive final result (with logging)

        Returns:
            Final assembled and polished output
        """
        self.structured_logger.info(
            "assemble_and_polish_details",
            num_results=len(results),
            plan_complexity=plan.complexity
        )

        result = super().assemble_and_polish(results, plan)

        self.structured_logger.info(
            "assembly_completed",
            final_length=len(result)
        )

        # Track model usage
        if self.metrics:
            self.metrics.record_model_usage(self.model)
            cost = self.get_cost()
            self.metrics.record_token_usage(
                self.model,
                self.input_tokens,
                self.output_tokens,
                cost
            )

        return result

    def get_orchestrator_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive orchestrator metrics

        Returns:
            Dictionary with all metrics and statistics
        """
        if not self.metrics:
            return {"error": "Metrics not enabled"}

        metrics_summary = self.metrics.get_metrics_summary()

        # Add orchestrator-specific stats
        metrics_summary['orchestrator'] = self.get_stats()

        return metrics_summary

    def save_metrics(self, filepath: str = 'logs/orchestrator_metrics.json'):
        """
        Save metrics to disk

        Args:
            filepath: Path to save metrics file
        """
        if self.metrics:
            self.metrics.save_to_disk(filepath)
            self.structured_logger.info(
                "metrics_saved",
                filepath=filepath
            )
        else:
            self.structured_logger.warning(
                "metrics_save_failed",
                reason="Metrics not enabled"
            )

    def reset_metrics(self):
        """Reset all metrics and statistics"""
        if self.metrics:
            self.metrics.reset_metrics()

        self.reset_stats()

        self.structured_logger.info("all_metrics_reset")
