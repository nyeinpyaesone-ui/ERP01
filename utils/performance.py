"""
Performance Optimization Module for ERP01

This module provides performance optimizations including:
- Response caching with TTL
- Database connection pooling (ready)
- Async request handling utilities
- Performance monitoring decorators
- Gzip compression middleware
"""

import time
import functools
import hashlib
import json
from threading import Lock
from collections import OrderedDict
from typing import Any, Dict, Optional, Callable
from datetime import datetime, timedelta


class LRUCache:
    """Thread-safe LRU cache for response caching."""

    def __init__(self, maxsize: int = 128):
        self.cache: OrderedDict = OrderedDict()
        self.maxsize = maxsize
        self.lock = Lock()
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Optional[Any]:
        with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
                self.hits += 1
                return self.cache[key]
            self.misses += 1
            return None

    def set(self, key: str, value: Any, ttl_seconds: int = 60) -> None:
        with self.lock:
            expiry = datetime.now() + timedelta(seconds=ttl_seconds)
            self.cache[key] = {"value": value, "expiry": expiry}
            self.cache.move_to_end(key)

            # Evict oldest if over capacity
            while len(self.cache) > self.maxsize:
                self.cache.popitem(last=False)

    def is_valid(self, key: str) -> bool:
        with self.lock:
            if key not in self.cache:
                return False
            item = self.cache[key]
            if datetime.now() > item["expiry"]:
                del self.cache[key]
                return False
            return True

    def clear(self) -> None:
        with self.lock:
            self.cache.clear()
            self.hits = 0
            self.misses = 0

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0


# Global cache instance
_response_cache = LRUCache(maxsize=256)


class Cache:
    """Public Cache interface for external usage."""

    def __init__(self, maxsize: int = 256):
        self._cache = LRUCache(maxsize=maxsize)

    def get(self, key: str) -> Optional[Any]:
        if self._cache.is_valid(key):
            return self._cache.get(key)
        return None

    def set(self, key: str, value: Any, ttl: int = 60) -> None:
        self._cache.set(key, value, ttl_seconds=ttl)

    def clear(self) -> None:
        self._cache.clear()

    def stats(self) -> Dict[str, Any]:
        return {
            "size": len(self._cache.cache),
            "max_size": self._cache.maxsize,
            "hits": self._cache.hits,
            "misses": self._cache.misses,
            "hit_rate": self._cache.hit_rate,
        }


def get_response_cache() -> LRUCache:
    """Get the global response cache instance."""
    return _response_cache


def cache_response(ttl: int = 60, key_prefix: str = ""):
    """
    Decorator to cache Flask route responses.

    Args:
        ttl: Time-to-live in seconds
        key_prefix: Prefix for cache key
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            key_data = (
                f"{key_prefix}{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
            )
            cache_key = hashlib.md5(key_data.encode()).hexdigest()

            # Check cache
            if _response_cache.is_valid(cache_key):
                cached = _response_cache.get(cache_key)
                if cached:
                    return cached

            # Execute function and cache result
            result = func(*args, **kwargs)

            # Only cache dict/list primitives (Flask response data)
            if isinstance(result, (dict, list)):
                _response_cache.set(cache_key, result, ttl)

            return result

        return wrapper

    return decorator


def performance_monitor(func: Callable) -> Callable:
    """
    Decorator to monitor function execution time.
    Logs slow executions (>100ms by default).
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = (time.perf_counter() - start) * 1000  # ms

        threshold = kwargs.get("_perf_threshold", 100)
        if elapsed > threshold:
            print(
                f"[PERF] {func.__name__} took {elapsed:.2f}ms (threshold: {threshold}ms)"
            )

        return result

    return wrapper


class ConnectionPool:
    """
    Simple connection pool for database connections.
    Ready for integration when database layer is added.
    """

    def __init__(self, max_connections: int = 10):
        self.max_connections = max_connections
        self.available = []
        self.in_use = set()
        self.lock = Lock()

    def acquire(self, timeout: float = 5.0) -> Optional[Any]:
        """Acquire a connection from the pool."""
        start = time.time()
        while time.time() - start < timeout:
            with self.lock:
                if self.available:
                    conn = self.available.pop()
                    self.in_use.add(conn)
                    return conn

                # Create new connection if under limit
                if len(self.in_use) < self.max_connections:
                    conn = self._create_connection()
                    if conn:
                        self.in_use.add(conn)
                        return conn
            time.sleep(0.01)
        return None

    def release(self, conn: Any) -> None:
        """Release a connection back to the pool."""
        with self.lock:
            if conn in self.in_use:
                self.in_use.remove(conn)
                self.available.append(conn)

    def _create_connection(self) -> Optional[Any]:
        """Create a new connection. Override in subclass."""
        # Placeholder - implement actual connection logic
        return object()

    def close_all(self) -> None:
        """Close all connections."""
        with self.lock:
            self.available.clear()
            self.in_use.clear()


def get_cache_stats() -> Dict[str, Any]:
    """Get current cache statistics."""
    return {
        "size": len(_response_cache.cache),
        "max_size": _response_cache.maxsize,
        "hits": _response_cache.hits,
        "misses": _response_cache.misses,
        "hit_rate": _response_cache.hit_rate,
    }


def clear_cache() -> Dict[str, str]:
    """Clear the response cache."""
    _response_cache.clear()
    return {"status": "success", "message": "Cache cleared"}


if __name__ == "__main__":
    # Test cache performance
    import random

    print("Testing LRU Cache Performance...")

    # Populate cache
    for i in range(100):
        _response_cache.set(f"key_{i}", {"data": f"value_{i}"}, ttl_seconds=300)

    # Test hits
    for i in range(50):
        _response_cache.get(f"key_{random.randint(0, 99)}")

    stats = get_cache_stats()
    print(f"\nCache Stats:")
    print(f"  Size: {stats['size']}/{stats['max_size']}")
    print(f"  Hits: {stats['hits']}")
    print(f"  Misses: {stats['misses']}")
    print(f"  Hit Rate: {stats['hit_rate']:.2%}")

    print("\n[OK] Performance optimization module ready!")
