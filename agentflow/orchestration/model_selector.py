"""
Dynamic Model Selection System

Intelligent task routing based on complexity analysis with cost/quality/speed optimization.
Tracks performance metrics per model and learns from historical data.
"""

import time
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from datetime import datetime
from collections import defaultdict

# Optional dependencies
try:
    import structlog
    logger = structlog.get_logger(__name__)
    HAS_STRUCTLOG = True
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    HAS_STRUCTLOG = False

try:
    from tenacity import retry, stop_after_attempt, wait_exponential
    HAS_TENACITY = True
except ImportError:
    # Fallback decorator if tenacity not available
    def retry(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    def stop_after_attempt(*args): pass
    def wait_exponential(*args, **kwargs): pass
    HAS_TENACITY = False


class ModelType(Enum):
    """Model selection categories"""
    SIMPLE = 'simple'
    MEDIUM = 'medium'
    COMPLEX = 'complex'
    SPEED_CRITICAL = 'speed_critical'


@dataclass
class ModelPerformanceMetrics:
    """Tracks performance metrics for individual models"""
    model_name: str
    total_cost: float = 0.0
    total_tokens: int = 0
    total_errors: int = 0
    total_requests: int = 0
    total_latency: float = 0.0
    quality_scores: List[float] = field(default_factory=list)
    last_used: Optional[datetime] = None

    def update_metrics(self,
                     cost: float,
                     tokens: int,
                     latency: float,
                     quality_score: Optional[float] = None,
                     is_error: bool = False) -> None:
        """Update metrics after a model execution"""
        self.total_cost += cost
        self.total_tokens += tokens
        self.total_latency += latency
        self.total_requests += 1
        self.last_used = datetime.now()

        if is_error:
            self.total_errors += 1
        if quality_score is not None:
            self.quality_scores.append(quality_score)

    def calculate_cost_per_token(self) -> float:
        """Calculate cost per token (in millicents)"""
        if self.total_tokens == 0:
            return 0.0
        return (self.total_cost * 1000) / self.total_tokens

    def get_performance_summary(self) -> Dict[str, Any]:
        """Return comprehensive performance summary"""
        avg_quality = sum(self.quality_scores) / len(self.quality_scores) if self.quality_scores else 0.0
        avg_latency = self.total_latency / self.total_requests if self.total_requests else 0.0

        return {
            'model_name': self.model_name,
            'total_cost': self.total_cost,
            'cost_per_token': self.calculate_cost_per_token(),
            'avg_latency': avg_latency,
            'error_rate': self.total_errors / self.total_requests if self.total_requests else 0.0,
            'avg_quality': avg_quality,
            'total_requests': self.total_requests,
            'last_used': self.last_used.isoformat() if self.last_used else None
        }


# Decision Matrix for task routing
DECISION_MATRIX = {
    'simple': {
        'provider': 'gpt-mini',
        'reason': 'Low complexity task - fast, cheap model optimal',
        'thresholds': {
            'max_context_size': 5000,
            'max_requirements': 3,
            'complexity_score': 3
        }
    },
    'medium': {
        'provider': 'deepseek',
        'reason': 'Medium complexity - balanced cost/quality',
        'thresholds': {
            'max_context_size': 15000,
            'max_requirements': 8,
            'complexity_score': 6
        }
    },
    'complex': {
        'provider': 'anthropic',
        'reason': 'High complexity - premium reasoning required',
        'thresholds': {
            'max_context_size': 50000,
            'max_requirements': float('inf'),
            'complexity_score': 10
        }
    },
    'speed_critical': {
        'provider': 'gpt-mini',
        'reason': 'Speed priority - fast model with minimal overhead',
        'thresholds': {
            'max_latency': 2.0
        }
    }
}


def calculate_weighted_score(cost: float, quality: float, speed: float,
                            weights: Dict[str, float]) -> float:
    """Calculate weighted score based on priorities"""
    # Normalize values to 0-1 range
    normalized_cost = 1 - min(max(cost, 0), 1)  # Lower is better
    normalized_quality = min(max(quality, 0), 1)  # Higher is better
    normalized_speed = 1 - min(max(speed, 0), 1)  # Lower is better

    return (
        weights.get('cost', 0.4) * normalized_cost +
        weights.get('quality', 0.4) * normalized_quality +
        weights.get('speed', 0.2) * normalized_speed
    )


def normalize_metrics(metrics: Dict[str, float], reference: Dict[str, float]) -> Dict[str, float]:
    """Normalize metrics against reference values"""
    return {
        'cost': metrics['cost'] / reference['cost'] if reference['cost'] else 1.0,
        'quality': metrics['quality'] / reference['quality'] if reference['quality'] else 1.0,
        'speed': metrics['speed'] / reference['speed'] if reference['speed'] else 1.0
    }


class ModelSelector:
    """
    Intelligent model selection with complexity analysis and performance tracking.

    Features:
    - Task complexity analysis (0-10 score)
    - Dynamic model routing based on requirements
    - Cost/quality/speed optimization
    - Performance tracking and learning
    """

    def __init__(self,
                 available_models: Optional[List[str]] = None,
                 default_weights: Optional[Dict[str, float]] = None,
                 enable_learning: bool = True):
        """
        Initialize ModelSelector

        Args:
            available_models: List of available model names
            default_weights: Default priority weights for selection
            enable_learning: Enable performance-based learning
        """
        self.available_models = available_models or [
            'gpt-mini', 'deepseek', 'anthropic', 'grok', 'claude'
        ]
        self.weights = default_weights or {'cost': 0.4, 'quality': 0.4, 'speed': 0.2}
        self.enable_learning = enable_learning

        # Performance tracking
        self.metrics = {
            model: ModelPerformanceMetrics(model)
            for model in self.available_models
        }

        # Reference metrics for normalization
        self.reference_metrics = {
            'cost': 0.01,    # $0.01 per 1K tokens baseline
            'quality': 0.8,  # 80% quality baseline
            'speed': 2.0     # 2s latency baseline
        }

        self.logger = logger

    def _analyze_complexity(self, task: Dict[str, Any]) -> int:
        """
        Analyze task complexity and return 0-10 score.

        Considers:
        - context_size: Length of task description and context
        - requirements_count: Number of requirements/constraints
        - task_type: Type of task (simple/medium/complex)

        Args:
            task: Task dictionary with description, context, requirements

        Returns:
            Complexity score (0-10)
        """
        score = 0

        # Factor 1: Context size (0-4 points)
        context_size = len(str(task.get('description', ''))) + len(str(task.get('context', '')))
        if context_size < 1000:
            score += 1
        elif context_size < 5000:
            score += 2
        elif context_size < 15000:
            score += 3
        else:
            score += 4

        # Factor 2: Requirements count (0-3 points)
        requirements = task.get('requirements', {})
        req_count = len(requirements.get('edge_cases', [])) + len(requirements.get('validation_criteria', []))
        if req_count <= 3:
            score += 1
        elif req_count <= 8:
            score += 2
        else:
            score += 3

        # Factor 3: Task type complexity (0-3 points)
        task_type = task.get('complexity', 'medium').lower()
        if task_type == 'low':
            score += 1
        elif task_type == 'medium':
            score += 2
        else:
            score += 3

        if HAS_STRUCTLOG:
            self.logger.info(
                "complexity_analysis",
                score=score,
                context_size=context_size,
                req_count=req_count,
                task_type=task_type
            )
        else:
            self.logger.info(
                f"Complexity analysis: score={score}, context_size={context_size}, "
                f"req_count={req_count}, task_type={task_type}"
            )

        return min(score, 10)

    def select_model_by_complexity(self, task: Dict[str, Any]) -> Tuple[str, str]:
        """
        Select model based on task complexity analysis.

        Args:
            task: Task dictionary to analyze

        Returns:
            Tuple of (provider_name, reason)
        """
        complexity_score = self._analyze_complexity(task)

        # Map complexity score to model type
        if complexity_score <= 3:
            model_type = 'simple'
        elif complexity_score <= 6:
            model_type = 'medium'
        elif task.get('speed_critical', False):
            model_type = 'speed_critical'
        else:
            model_type = 'complex'

        decision = DECISION_MATRIX[model_type]

        if HAS_STRUCTLOG:
            self.logger.info(
                "model_selection",
                complexity_score=complexity_score,
                model_type=model_type,
                provider=decision['provider'],
                reason=decision['reason']
            )
        else:
            self.logger.info(
                f"Model selection: complexity={complexity_score}, type={model_type}, "
                f"provider={decision['provider']}, reason={decision['reason']}"
            )

        return decision['provider'], decision['reason']

    def track_execution(self, model_name: str):
        """
        Decorator to track model execution metrics.

        Usage:
            @selector.track_execution('gpt-mini')
            def call_model():
                ...
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    latency = time.time() - start_time

                    # Extract cost and tokens from response if available
                    cost = result.get('cost', 0.0) if isinstance(result, dict) else 0.0
                    tokens = result.get('tokens', 0) if isinstance(result, dict) else 0
                    quality = result.get('quality_score', None) if isinstance(result, dict) else None

                    if self.enable_learning and model_name in self.metrics:
                        self.metrics[model_name].update_metrics(
                            cost=cost,
                            tokens=tokens,
                            latency=latency,
                            quality_score=quality
                        )

                    if HAS_STRUCTLOG:
                        self.logger.info(
                            "execution_tracked",
                            model=model_name,
                            latency=latency,
                            cost=cost,
                            tokens=tokens
                        )
                    else:
                        self.logger.info(
                            f"Execution tracked: model={model_name}, latency={latency}, "
                            f"cost={cost}, tokens={tokens}"
                        )

                    return result

                except Exception as e:
                    latency = time.time() - start_time
                    if self.enable_learning and model_name in self.metrics:
                        self.metrics[model_name].update_metrics(
                            cost=0.0,
                            tokens=0,
                            latency=latency,
                            is_error=True
                        )

                    if HAS_STRUCTLOG:
                        self.logger.error(
                            "execution_failed",
                            model=model_name,
                            error=str(e),
                            latency=latency
                        )
                    else:
                        self.logger.error(
                            f"Execution failed: model={model_name}, error={e}, latency={latency}"
                        )
                    raise e

            return wrapper
        return decorator

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def select_model(self, task_requirements: Dict[str, Any]) -> str:
        """
        Select best model based on current metrics and task requirements.

        Uses performance history to optimize selection over time.

        Args:
            task_requirements: Task requirements including priority, constraints

        Returns:
            Selected model name
        """
        if not self.enable_learning or not self.metrics:
            # Fallback to complexity-based selection
            model, _ = self.select_model_by_complexity(task_requirements)
            return model

        # Get performance summaries for all models with data
        summaries = {}
        for model, metrics in self.metrics.items():
            if metrics.total_requests > 0:
                summaries[model] = metrics.get_performance_summary()

        if not summaries:
            # No historical data, use complexity analysis
            model, _ = self.select_model_by_complexity(task_requirements)
            return model

        # Calculate weighted scores for each model
        scores = {}
        for model, summary in summaries.items():
            normalized = normalize_metrics({
                'cost': summary['cost_per_token'],
                'quality': summary['avg_quality'],
                'speed': summary['avg_latency']
            }, self.reference_metrics)

            # Adjust weights based on task requirements
            weights = self.weights.copy()
            if 'priority' in task_requirements:
                priority = task_requirements['priority']
                if priority == 'cost':
                    weights = {'cost': 0.6, 'quality': 0.3, 'speed': 0.1}
                elif priority == 'quality':
                    weights = {'cost': 0.2, 'quality': 0.7, 'speed': 0.1}
                elif priority == 'speed':
                    weights = {'cost': 0.3, 'quality': 0.2, 'speed': 0.5}

            scores[model] = calculate_weighted_score(
                cost=normalized['cost'],
                quality=normalized['quality'],
                speed=normalized['speed'],
                weights=weights
            )

        # Return model with highest score
        best_model = max(scores.items(), key=lambda x: x[1])[0]

        if HAS_STRUCTLOG:
            self.logger.info(
                "learned_model_selection",
                selected_model=best_model,
                scores=scores,
                priority=task_requirements.get('priority', 'balanced')
            )
        else:
            self.logger.info(
                f"Learned model selection: selected={best_model}, "
                f"priority={task_requirements.get('priority', 'balanced')}"
            )

        return best_model

    def optimize_selection(self,
                          target_cost: float,
                          min_quality: float,
                          max_latency: float) -> List[Tuple[str, Dict]]:
        """
        Find models that meet specified constraints.

        Args:
            target_cost: Maximum cost per token (millicents)
            min_quality: Minimum quality score (0-1)
            max_latency: Maximum latency in seconds

        Returns:
            List of (model_name, summary) tuples meeting constraints
        """
        valid_models = []

        for model, metrics in self.metrics.items():
            if metrics.total_requests == 0:
                continue

            summary = metrics.get_performance_summary()

            if (summary['cost_per_token'] <= target_cost and
                summary['avg_quality'] >= min_quality and
                summary['avg_latency'] <= max_latency):
                valid_models.append((model, summary))

        # Sort by quality descending
        valid_models.sort(key=lambda x: x[1]['avg_quality'], reverse=True)

        if HAS_STRUCTLOG:
            self.logger.info(
                "optimization_results",
                valid_models_count=len(valid_models),
                constraints={
                    'cost': target_cost,
                    'quality': min_quality,
                    'latency': max_latency
                }
            )
        else:
            self.logger.info(
                f"Optimization results: found {len(valid_models)} models meeting constraints"
            )

        return valid_models

    def get_best_model(self, priority: str = 'balanced') -> str:
        """
        Quick access to best model based on priority.

        Args:
            priority: 'cost', 'quality', 'speed', or 'balanced'

        Returns:
            Best model name
        """
        return self.select_model({'priority': priority})

    def record_quality_score(self, model_name: str, score: float):
        """
        Record quality score for a completed task.

        Args:
            model_name: Model that generated the output
            score: Quality score (0-1)
        """
        if model_name in self.metrics and self.enable_learning:
            self.metrics[model_name].quality_scores.append(score)

            avg_quality = sum(self.metrics[model_name].quality_scores) / len(self.metrics[model_name].quality_scores)
            if HAS_STRUCTLOG:
                self.logger.info(
                    "quality_recorded",
                    model=model_name,
                    score=score,
                    avg_quality=avg_quality
                )
            else:
                self.logger.info(
                    f"Quality recorded: model={model_name}, score={score}, avg={avg_quality}"
                )

    def get_performance_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive performance report.

        Returns:
            Report with all model metrics and recommendations
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'models': {},
            'recommendations': {}
        }

        for model, metrics in self.metrics.items():
            if metrics.total_requests > 0:
                report['models'][model] = metrics.get_performance_summary()

        # Generate recommendations
        if report['models']:
            # Best for cost
            cost_sorted = sorted(
                report['models'].items(),
                key=lambda x: x[1]['cost_per_token']
            )
            report['recommendations']['best_for_cost'] = cost_sorted[0][0] if cost_sorted else None

            # Best for quality
            quality_sorted = sorted(
                report['models'].items(),
                key=lambda x: x[1]['avg_quality'],
                reverse=True
            )
            report['recommendations']['best_for_quality'] = quality_sorted[0][0] if quality_sorted else None

            # Best for speed
            speed_sorted = sorted(
                report['models'].items(),
                key=lambda x: x[1]['avg_latency']
            )
            report['recommendations']['best_for_speed'] = speed_sorted[0][0] if speed_sorted else None

        self.logger.info("performance_report_generated", models_count=len(report['models']))

        return report

    def reset_metrics(self):
        """Reset all performance metrics"""
        for metrics in self.metrics.values():
            metrics.total_cost = 0.0
            metrics.total_tokens = 0
            metrics.total_errors = 0
            metrics.total_requests = 0
            metrics.total_latency = 0.0
            metrics.quality_scores.clear()
            metrics.last_used = None

        self.logger.info("metrics_reset")

    def save_metrics(self, file_path: str):
        """
        Save metrics to JSON file.

        Args:
            file_path: Path to save metrics
        """
        report = self.get_performance_report()

        with open(file_path, 'w') as f:
            json.dump(report, f, indent=2)

        self.logger.info("metrics_saved", file_path=file_path)

    def load_metrics(self, file_path: str):
        """
        Load metrics from JSON file.

        Args:
            file_path: Path to load metrics from
        """
        with open(file_path, 'r') as f:
            report = json.load(f)

        # Restore metrics
        for model_name, summary in report.get('models', {}).items():
            if model_name in self.metrics:
                metrics = self.metrics[model_name]
                metrics.total_cost = summary['total_cost']
                metrics.total_tokens = int(summary['cost_per_token'] * summary['total_cost'] * 1000) if summary['cost_per_token'] else 0
                metrics.total_requests = summary['total_requests']
                metrics.total_latency = summary['avg_latency'] * summary['total_requests']
                metrics.total_errors = int(summary['error_rate'] * summary['total_requests'])
                if summary['last_used']:
                    metrics.last_used = datetime.fromisoformat(summary['last_used'])

        self.logger.info("metrics_loaded", file_path=file_path)
