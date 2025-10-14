"""
Error Handler - Standardized Error Handling

Provides consistent error handling across all integrations.
"""

import logging
from typing import Optional, Dict, Any
from enum import Enum


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IntegrationError(Exception):
    """Base exception for all integration errors"""

    def __init__(
        self,
        message: str,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None
    ):
        super().__init__(message)
        self.severity = severity
        self.details = details or {}
        self.original_error = original_error

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary"""
        return {
            'error': self.__class__.__name__,
            'message': str(self),
            'severity': self.severity.value,
            'details': self.details
        }


class APIError(IntegrationError):
    """API-related errors"""
    pass


class AuthenticationError(IntegrationError):
    """Authentication errors"""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, severity=ErrorSeverity.HIGH, **kwargs)


class RateLimitError(IntegrationError):
    """Rate limit exceeded errors"""
    def __init__(self, message: str, retry_after: Optional[int] = None, **kwargs):
        super().__init__(message, severity=ErrorSeverity.MEDIUM, **kwargs)
        self.retry_after = retry_after


class ValidationError(IntegrationError):
    """Data validation errors"""
    pass


class ConfigurationError(IntegrationError):
    """Configuration errors"""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, severity=ErrorSeverity.CRITICAL, **kwargs)


class ErrorHandler:
    """
    Standardized error handler

    Features:
    - Error logging with context
    - Error transformation
    - Retry decision logic
    - Error aggregation
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize error handler

        Args:
            logger: Logger instance (creates new if None)
        """
        self.logger = logger or logging.getLogger(__name__)
        self.error_counts: Dict[str, int] = {}

    def handle(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        reraise: bool = True
    ):
        """
        Handle error with logging and context

        Args:
            error: Exception to handle
            context: Additional context information
            reraise: Whether to re-raise the error

        Raises:
            Exception: Original error if reraise=True
        """
        context = context or {}

        # Track error count
        error_type = error.__class__.__name__
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1

        # Determine severity
        if isinstance(error, IntegrationError):
            severity = error.severity
        else:
            severity = self._determine_severity(error)

        # Log error
        log_message = f"{error_type}: {str(error)}"
        if context:
            log_message += f" | Context: {context}"

        if severity == ErrorSeverity.CRITICAL:
            self.logger.critical(log_message, exc_info=True)
        elif severity == ErrorSeverity.HIGH:
            self.logger.error(log_message, exc_info=True)
        elif severity == ErrorSeverity.MEDIUM:
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)

        if reraise:
            raise error

    def _determine_severity(self, error: Exception) -> ErrorSeverity:
        """Determine error severity from exception type"""
        error_name = error.__class__.__name__.lower()

        if 'auth' in error_name or 'permission' in error_name:
            return ErrorSeverity.HIGH
        elif 'timeout' in error_name or 'connection' in error_name:
            return ErrorSeverity.MEDIUM
        elif 'validation' in error_name or 'value' in error_name:
            return ErrorSeverity.LOW
        else:
            return ErrorSeverity.MEDIUM

    def should_retry(self, error: Exception, attempt: int, max_attempts: int) -> bool:
        """
        Determine if operation should be retried

        Args:
            error: Exception that occurred
            attempt: Current attempt number (0-indexed)
            max_attempts: Maximum number of attempts

        Returns:
            True if should retry, False otherwise
        """
        # Don't retry if out of attempts
        if attempt >= max_attempts - 1:
            return False

        # Don't retry on authentication errors
        if isinstance(error, AuthenticationError):
            return False

        # Don't retry on validation errors
        if isinstance(error, ValidationError):
            return False

        # Don't retry on configuration errors
        if isinstance(error, ConfigurationError):
            return False

        # Retry on rate limit errors (with backoff)
        if isinstance(error, RateLimitError):
            return True

        # Retry on API errors
        if isinstance(error, APIError):
            return True

        # Retry on network errors
        error_name = error.__class__.__name__.lower()
        if any(x in error_name for x in ['timeout', 'connection', 'network']):
            return True

        # Default: don't retry
        return False

    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics"""
        total_errors = sum(self.error_counts.values())
        return {
            'total_errors': total_errors,
            'by_type': self.error_counts.copy(),
            'unique_types': len(self.error_counts)
        }

    def reset_stats(self):
        """Reset error statistics"""
        self.error_counts.clear()
