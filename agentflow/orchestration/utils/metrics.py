"""
Metrics Collector - Performance and Cost Tracking

Tracks metrics for integration operations:
- Call counts and success rates
- Latency tracking
- Cost tracking
- Error rates
"""

import time
import threading
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from contextlib import contextmanager


@dataclass
class OperationMetrics:
    """Metrics for a single operation type"""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    total_latency: float = 0.0
    total_cost: float = 0.0

    @property
    def success_rate(self) -> float:
        if self.total_calls == 0:
            return 0.0
        return self.successful_calls / self.total_calls

    @property
    def avg_latency(self) -> float:
        if self.total_calls == 0:
            return 0.0
        return self.total_latency / self.total_calls

    @property
    def avg_cost(self) -> float:
        if self.total_calls == 0:
            return 0.0
        return self.total_cost / self.total_calls

    def to_dict(self) -> Dict[str, Any]:
        return {
            'total_calls': self.total_calls,
            'successful_calls': self.successful_calls,
            'failed_calls': self.failed_calls,
            'success_rate': round(self.success_rate, 4),
            'avg_latency': round(self.avg_latency, 4),
            'avg_cost': round(self.avg_cost, 6),
            'total_cost': round(self.total_cost, 6)
        }


class MetricsCollector:
    """
    Performance and cost metrics collector

    Features:
    - Thread-safe metrics tracking
    - Per-operation metrics
    - Context manager for automatic tracking
    - Real-time metrics access
    """

    def __init__(self):
        self.operations: Dict[str, OperationMetrics] = {}
        self.lock = threading.Lock()

    @contextmanager
    def track(self, operation: str, cost: float = 0.0):
        """
        Context manager for tracking operation

        Usage:
            with metrics.track('api_call', cost=0.001):
                result = api.call()

        Args:
            operation: Operation name
            cost: Operation cost (optional)
        """
        start_time = time.time()
        success = False

        try:
            yield
            success = True
        finally:
            latency = time.time() - start_time
            self._record(operation, success, latency, cost)

    def _record(
        self,
        operation: str,
        success: bool,
        latency: float,
        cost: float
    ):
        """Record operation metrics"""
        with self.lock:
            if operation not in self.operations:
                self.operations[operation] = OperationMetrics()

            metrics = self.operations[operation]
            metrics.total_calls += 1
            if success:
                metrics.successful_calls += 1
            else:
                metrics.failed_calls += 1
            metrics.total_latency += latency
            metrics.total_cost += cost

    def record_call(
        self,
        operation: str,
        success: bool = True,
        latency: float = 0.0,
        cost: float = 0.0
    ):
        """
        Manually record operation metrics

        Args:
            operation: Operation name
            success: Whether operation succeeded
            latency: Operation latency in seconds
            cost: Operation cost in dollars
        """
        self._record(operation, success, latency, cost)

    def get_metrics(self, operation: Optional[str] = None) -> Dict[str, Any]:
        """
        Get metrics summary

        Args:
            operation: Specific operation name (None for all)

        Returns:
            Metrics dictionary
        """
        with self.lock:
            if operation:
                if operation not in self.operations:
                    return {}
                return {operation: self.operations[operation].to_dict()}

            # Return all metrics
            return {
                op: metrics.to_dict()
                for op, metrics in self.operations.items()
            }

    def get_total_metrics(self) -> Dict[str, Any]:
        """Get aggregated metrics across all operations"""
        with self.lock:
            total_calls = sum(m.total_calls for m in self.operations.values())
            successful_calls = sum(m.successful_calls for m in self.operations.values())
            failed_calls = sum(m.failed_calls for m in self.operations.values())
            total_latency = sum(m.total_latency for m in self.operations.values())
            total_cost = sum(m.total_cost for m in self.operations.values())

            return {
                'total_calls': total_calls,
                'successful_calls': successful_calls,
                'failed_calls': failed_calls,
                'success_rate': round(successful_calls / total_calls if total_calls > 0 else 0, 4),
                'avg_latency': round(total_latency / total_calls if total_calls > 0 else 0, 4),
                'total_cost': round(total_cost, 6),
                'operation_count': len(self.operations)
            }

    def reset(self, operation: Optional[str] = None):
        """
        Reset metrics

        Args:
            operation: Specific operation to reset (None for all)
        """
        with self.lock:
            if operation:
                if operation in self.operations:
                    del self.operations[operation]
            else:
                self.operations.clear()
