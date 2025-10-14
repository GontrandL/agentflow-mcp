"""
Rate Limiter - Token Bucket Rate Limiting

Implements token bucket algorithm for API rate limiting.
"""

import time
import threading
from typing import Optional


class RateLimiter:
    """
    Token bucket rate limiter

    Features:
    - Thread-safe implementation
    - Configurable rate and burst size
    - Context manager support
    - Automatic token refill
    """

    def __init__(
        self,
        calls_per_minute: int = 100,
        burst_size: Optional[int] = None
    ):
        """
        Initialize rate limiter

        Args:
            calls_per_minute: Maximum calls per minute
            burst_size: Maximum burst size (defaults to calls_per_minute)
        """
        self.calls_per_minute = calls_per_minute
        self.burst_size = burst_size or calls_per_minute
        self.tokens = self.burst_size
        self.last_update = time.time()
        self.lock = threading.Lock()

    def __enter__(self):
        """Context manager entry - wait for token"""
        self.acquire()
        return self

    def __exit__(self, *args):
        """Context manager exit"""
        pass

    def acquire(self, tokens: int = 1):
        """
        Acquire tokens (blocking)

        Args:
            tokens: Number of tokens to acquire
        """
        while True:
            with self.lock:
                self._refill_tokens()

                if self.tokens >= tokens:
                    self.tokens -= tokens
                    return

                # Calculate wait time
                tokens_needed = tokens - self.tokens
                wait_time = (tokens_needed / self.calls_per_minute) * 60

            # Wait outside lock
            time.sleep(wait_time)

    def try_acquire(self, tokens: int = 1) -> bool:
        """
        Try to acquire tokens (non-blocking)

        Args:
            tokens: Number of tokens to acquire

        Returns:
            True if acquired, False otherwise
        """
        with self.lock:
            self._refill_tokens()

            if self.tokens >= tokens:
                self.tokens -= tokens
                return True

            return False

    def _refill_tokens(self):
        """Refill tokens based on elapsed time"""
        now = time.time()
        elapsed = now - self.last_update

        # Refill tokens
        new_tokens = (elapsed / 60) * self.calls_per_minute
        self.tokens = min(self.burst_size, self.tokens + new_tokens)
        self.last_update = now

    def get_available_tokens(self) -> float:
        """Get number of currently available tokens"""
        with self.lock:
            self._refill_tokens()
            return self.tokens

    def wait_time(self, tokens: int = 1) -> float:
        """
        Get estimated wait time for tokens

        Args:
            tokens: Number of tokens needed

        Returns:
            Wait time in seconds
        """
        with self.lock:
            self._refill_tokens()

            if self.tokens >= tokens:
                return 0.0

            tokens_needed = tokens - self.tokens
            return (tokens_needed / self.calls_per_minute) * 60
