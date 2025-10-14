"""
Smart Orchestration Module

Provides intelligent orchestration with powerful models (Claude, GPT-4, etc.)
coordinating cheap/free worker models for optimal cost/quality balance.

Features:
- Dynamic model selection based on task complexity
- Cost/quality/speed optimization
- Performance tracking and learning
- Automatic fallback chain handling
- Structured logging and real-time metrics
"""

# Core orchestration
from .smart_orchestrator import (
    SmartOrchestrator,
    Subtask,
    Plan,
    ValidationResult
)
from .model_selector import ModelSelector

# Enhanced orchestration with logging & metrics
try:
    from .smart_orchestrator_logging import SmartOrchestratorWithLogging
except ImportError:
    SmartOrchestratorWithLogging = None

# Logging configuration
try:
    from .logging_config import (
        setup_structlog,
        get_logger,
        configure_orchestrator_logging,
        LOG_LEVELS
    )
except ImportError:
    setup_structlog = None
    get_logger = None
    configure_orchestrator_logging = None
    LOG_LEVELS = None

# Metrics tracking
try:
    from .metrics import (
        OrchestratorMetrics,
        Metric,
        MetricType
    )
except ImportError:
    OrchestratorMetrics = None
    Metric = None
    MetricType = None

__all__ = [
    # Core orchestration
    'SmartOrchestrator',
    'Subtask',
    'Plan',
    'ValidationResult',
    'ModelSelector',

    # Enhanced with logging/metrics (if available)
    'SmartOrchestratorWithLogging',

    # Logging (if available)
    'setup_structlog',
    'get_logger',
    'configure_orchestrator_logging',
    'LOG_LEVELS',

    # Metrics (if available)
    'OrchestratorMetrics',
    'Metric',
    'MetricType',
]
