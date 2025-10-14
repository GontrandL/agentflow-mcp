"""
Retry Helper - Exponential Backoff Retry Logic

Provides decorators and context managers for automatic retry
with exponential backoff.
"""

import time
import logging
from typing import Callable, Optional, Type, Tuple
from functools import wraps

logger = logging.getLogger(__name__)


class RetryHelper:
    """
    Exponential backoff retry helper

    Features:
    - Configurable max attempts
    - Exponential backoff (2^n)
    - Selective exception handling
    - Logging support
    """

    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 2.0,
        max_delay: float = 60.0,
        exceptions: Tuple[Type[Exception], ...] = (Exception,)
    ):
        """
        Initialize retry helper

        Args:
            max_attempts: Maximum number of retry attempts
            base_delay: Base delay in seconds (doubles each retry)
            max_delay: Maximum delay between retries
            exceptions: Tuple of exception types to catch
        """
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exceptions = exceptions

    def __call__(self, func: Callable) -> Callable:
        """Decorator for automatic retry"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(self.max_attempts):
                try:
                    return func(*args, **kwargs)

                except self.exceptions as e:
                    last_exception = e

                    if attempt < self.max_attempts - 1:
                        delay = min(
                            self.base_delay * (2 ** attempt),
                            self.max_delay
                        )
                        logger.warning(
                            f"Attempt {attempt + 1}/{self.max_attempts} failed: {e}. "
                            f"Retrying in {delay}s..."
                        )
                        time.sleep(delay)
                    else:
                        logger.error(
                            f"All {self.max_attempts} attempts failed. "
                            f"Last error: {e}"
                        )

            raise last_exception

        return wrapper

    def execute(self, func: Callable, *args, **kwargs):
        """Execute function with retry"""
        return self(func)(*args, **kwargs)


def retry_exponential(
    max_attempts: int = 3,
    base_delay: float = 2.0,
    max_delay: float = 60.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """
    Convenience decorator for exponential backoff retry

    Usage:
        @retry_exponential(max_attempts=3)
        def my_function():
            # function code
            pass
    """
    return RetryHelper(
        max_attempts=max_attempts,
        base_delay=base_delay,
        max_delay=max_delay,
        exceptions=exceptions
    )
