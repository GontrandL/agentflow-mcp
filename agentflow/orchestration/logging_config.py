"""
Structured logging configuration for AgentFlow orchestration

Provides JSON-formatted structured logging with configurable levels
for console and file output, optimized for production monitoring.
"""

import structlog
import logging
import sys
from pathlib import Path
from typing import Optional
from structlog import configure
from structlog.processors import (
    JSONRenderer,
    TimeStamper,
    add_log_level,
    StackInfoRenderer,
    format_exc_info
)
from structlog.stdlib import (
    add_logger_name,
    filter_by_level,
    ProcessorFormatter
)


def setup_structlog(
    log_level: str = 'INFO',
    log_file: Optional[str] = None,
    enable_console: bool = True
) -> None:
    """
    Configure structlog with JSON formatter and appropriate log levels.

    Args:
        log_level: The logging level to set (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for log output
        enable_console: Whether to enable console output (default: True)

    Example:
        >>> setup_structlog(log_level='DEBUG', log_file='logs/orchestrator.log')
    """
    # Validate log level
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {log_level}')

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        level=numeric_level,
        handlers=[]  # We'll add handlers manually
    )

    # Create handlers
    handlers = []

    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        handlers.append(console_handler)

    if log_file:
        # Create log directory if it doesn't exist
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(numeric_level)
        handlers.append(file_handler)

    # Configure root logger with handlers
    root_logger = logging.getLogger()
    root_logger.handlers = handlers
    root_logger.setLevel(numeric_level)

    # Configure structlog processors
    shared_processors = [
        filter_by_level,
        add_log_level,
        add_logger_name,
        TimeStamper(fmt='iso', utc=True),
        StackInfoRenderer(),
        format_exc_info,
    ]

    # Configure structlog
    configure(
        processors=shared_processors + [
            ProcessorFormatter.wrap_for_formatter,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True
    )

    # Configure the ProcessorFormatter for JSON output
    formatter = ProcessorFormatter(
        processor=JSONRenderer(indent=None),  # Compact JSON for production
        foreign_pre_chain=shared_processors,
    )

    for handler in handlers:
        handler.setFormatter(formatter)


def get_logger(name: str) -> structlog.BoundLogger:
    """
    Retrieve a configured logger instance.

    Args:
        name: The name of the logger (typically __name__ of the module)

    Returns:
        structlog.BoundLogger: A configured logger instance with bound context

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("task_started", task_id="task_1", complexity="high")
    """
    return structlog.get_logger(name)


def configure_orchestrator_logging(
    log_level: str = 'INFO',
    log_dir: Optional[str] = None
) -> structlog.BoundLogger:
    """
    Convenience function to configure logging for orchestrator with sensible defaults.

    Args:
        log_level: Logging level (default: INFO)
        log_dir: Directory for log files (default: logs/)

    Returns:
        Configured logger instance for the orchestrator

    Example:
        >>> logger = configure_orchestrator_logging(log_level='DEBUG')
        >>> logger.info("orchestrator_initialized", provider="anthropic")
    """
    if log_dir:
        log_file = f"{log_dir}/orchestrator.log"
    else:
        log_file = "logs/orchestrator.log"

    setup_structlog(
        log_level=log_level,
        log_file=log_file,
        enable_console=True
    )

    return get_logger('agentflow.orchestration')


# Log level constants for convenience
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}
