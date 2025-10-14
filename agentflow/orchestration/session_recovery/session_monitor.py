"""
Session Monitor - Real-time context usage tracking

Monitors session health and triggers recovery preparation at 80% context usage.
Implements four-tier pressure system from research report.
"""

import time
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class SessionMetrics:
    """Session health metrics"""
    tokens_used: int
    tokens_available: int
    usage_percentage: float
    pressure_level: str
    time_active: float
    last_checkpoint: Optional[float] = None


class SessionMonitor:
    """
    Monitor session context usage and trigger recovery preparation

    Four-tier pressure system:
    - NORMAL: <60% usage
    - ELEVATED: 60-80% usage (warning)
    - CRITICAL: 80-90% usage (prepare recovery)
    - EMERGENCY: >90% usage (force recovery)
    """

    def __init__(self, context_limit: int = 200000, warning_threshold: float = 0.8):
        """
        Initialize session monitor

        Args:
            context_limit: Maximum context window size (default: 200K tokens)
            warning_threshold: Trigger recovery at this percentage (default: 0.8 = 80%)
        """
        self.context_limit = context_limit
        self.warning_threshold = warning_threshold
        self.current_usage = 0
        self.start_time = time.time()
        self.last_checkpoint = None

    def track_usage(self, conversation_history: str = "") -> SessionMetrics:
        """
        Track current context window usage

        Args:
            conversation_history: Current conversation to measure

        Returns:
            SessionMetrics with current usage statistics
        """
        # Estimate tokens (rough: 1 token ≈ 4 characters)
        self.current_usage = len(conversation_history) // 4

        metrics = SessionMetrics(
            tokens_used=self.current_usage,
            tokens_available=self.context_limit - self.current_usage,
            usage_percentage=self.current_usage / self.context_limit,
            pressure_level=self._get_pressure_level(),
            time_active=time.time() - self.start_time,
            last_checkpoint=self.last_checkpoint
        )

        return metrics

    def should_prepare_recovery(self, metrics: Optional[SessionMetrics] = None) -> bool:
        """
        Check if we need to prepare session recovery

        Args:
            metrics: Optional pre-computed metrics

        Returns:
            True if recovery preparation should be triggered
        """
        if metrics is None:
            metrics = self.track_usage()

        # Trigger at warning threshold (default 80%)
        return metrics.usage_percentage >= self.warning_threshold

    def should_force_recovery(self, metrics: Optional[SessionMetrics] = None) -> bool:
        """
        Check if we need to force immediate recovery (emergency)

        Args:
            metrics: Optional pre-computed metrics

        Returns:
            True if emergency recovery is required
        """
        if metrics is None:
            metrics = self.track_usage()

        # Emergency at 90%
        return metrics.usage_percentage >= 0.90

    def mark_checkpoint(self):
        """Mark that a recovery checkpoint was created"""
        self.last_checkpoint = time.time()

    def _get_pressure_level(self) -> str:
        """
        Determine context pressure level

        Returns:
            NORMAL | ELEVATED | CRITICAL | EMERGENCY
        """
        usage_pct = self.current_usage / self.context_limit

        if usage_pct < 0.60:
            return 'NORMAL'
        elif usage_pct < 0.80:
            return 'ELEVATED'
        elif usage_pct < 0.90:
            return 'CRITICAL'
        else:
            return 'EMERGENCY'

    def get_status_report(self, metrics: Optional[SessionMetrics] = None) -> str:
        """
        Generate human-readable status report

        Args:
            metrics: Optional pre-computed metrics

        Returns:
            Formatted status report string
        """
        if metrics is None:
            metrics = self.track_usage()

        status_emoji = {
            'NORMAL': '✅',
            'ELEVATED': '⚠️',
            'CRITICAL': '🔴',
            'EMERGENCY': '🚨'
        }

        checkpoint_info = f"{(time.time() - metrics.last_checkpoint) / 60:.1f} min ago" if metrics.last_checkpoint else "Never"
        recovery_warning = "⚠️  PREPARE RECOVERY SOON" if self.should_prepare_recovery(metrics) else ""
        force_warning = "🚨 FORCE RECOVERY NOW!" if self.should_force_recovery(metrics) else ""

        return f"""
📊 Session Health Report

Status: {status_emoji[metrics.pressure_level]} {metrics.pressure_level}
Context: {metrics.tokens_used:,} / {self.context_limit:,} tokens ({metrics.usage_percentage:.1%})
Available: {metrics.tokens_available:,} tokens
Active: {metrics.time_active / 60:.1f} minutes
Last Checkpoint: {checkpoint_info}

{recovery_warning}
{force_warning}
"""


# Example usage
if __name__ == "__main__":
    monitor = SessionMonitor()

    # Simulate session growth
    fake_history = "x" * 160000  # ~40K tokens
    metrics = monitor.track_usage(fake_history)

    print(monitor.get_status_report(metrics))
    print(f"Should prepare recovery: {monitor.should_prepare_recovery(metrics)}")
    print(f"Should force recovery: {monitor.should_force_recovery(metrics)}")
