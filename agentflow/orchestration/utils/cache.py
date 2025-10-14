"""
Cache Manager - Intelligent Caching with TTL

Provides in-memory caching with time-to-live support.
"""

import time
import threading
from typing import Any, Optional, Callable
from dataclasses import dataclass
from functools import wraps


@dataclass
class CacheEntry:
    """Single cache entry with TTL"""
    value: Any
    timestamp: float
    ttl: float

    def is_expired(self) -> bool:
        """Check if entry has expired"""
        if self.ttl <= 0:
            return False  # Never expires
        return time.time() - self.timestamp > self.ttl


class CacheManager:
    """
    In-memory cache with TTL support

    Features:
    - Thread-safe operations
    - TTL-based expiration
    - LRU-style automatic cleanup
    - Decorator support
    """

    def __init__(self, default_ttl: float = 3600, max_size: int = 1000):
        """
        Initialize cache manager

        Args:
            default_ttl: Default time-to-live in seconds
            max_size: Maximum number of cache entries
        """
        self.default_ttl = default_ttl
        self.max_size = max_size
        self._cache = {}
        self.lock = threading.Lock()
        self._hits = 0
        self._misses = 0

    def get(self, key: str, default: Any = None) -> Optional[Any]:
        """
        Get value from cache

        Args:
            key: Cache key
            default: Default value if not found

        Returns:
            Cached value or default
        """
        with self.lock:
            if key in self._cache:
                entry = self._cache[key]
                if not entry.is_expired():
                    self._hits += 1
                    return entry.value
                else:
                    # Remove expired entry
                    del self._cache[key]

            self._misses += 1
            return default

    def set(self, key: str, value: Any, ttl: Optional[float] = None):
        """
        Set value in cache

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (None for default)
        """
        with self.lock:
            # Cleanup if at capacity
            if len(self._cache) >= self.max_size:
                self._cleanup()

            ttl = ttl if ttl is not None else self.default_ttl
            self._cache[key] = CacheEntry(
                value=value,
                timestamp=time.time(),
                ttl=ttl
            )

    def delete(self, key: str):
        """Delete key from cache"""
        with self.lock:
            if key in self._cache:
                del self._cache[key]

    def clear(self):
        """Clear entire cache"""
        with self.lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0

    def _cleanup(self):
        """Remove expired entries"""
        now = time.time()
        expired_keys = [
            key for key, entry in self._cache.items()
            if entry.ttl > 0 and now - entry.timestamp > entry.ttl
        ]

        for key in expired_keys:
            del self._cache[key]

        # If still at capacity, remove oldest entries
        if len(self._cache) >= self.max_size:
            # Sort by timestamp, remove oldest 10%
            sorted_items = sorted(
                self._cache.items(),
                key=lambda x: x[1].timestamp
            )
            remove_count = max(1, len(sorted_items) // 10)
            for key, _ in sorted_items[:remove_count]:
                del self._cache[key]

    def get_stats(self) -> dict:
        """Get cache statistics"""
        with self.lock:
            total = self._hits + self._misses
            hit_rate = self._hits / total if total > 0 else 0

            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'hits': self._hits,
                'misses': self._misses,
                'hit_rate': round(hit_rate, 4),
                'default_ttl': self.default_ttl
            }

    def cached(self, ttl: Optional[float] = None, key_func: Optional[Callable] = None):
        """
        Decorator for caching function results

        Usage:
            @cache.cached(ttl=3600)
            def expensive_function(arg):
                return result

        Args:
            ttl: Cache TTL in seconds
            key_func: Function to generate cache key from args
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    cache_key = f"{func.__name__}:{args}:{kwargs}"

                # Check cache
                cached_value = self.get(cache_key)
                if cached_value is not None:
                    return cached_value

                # Call function and cache result
                result = func(*args, **kwargs)
                self.set(cache_key, result, ttl=ttl)
                return result

            return wrapper
        return decorator
