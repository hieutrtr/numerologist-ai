"""
Redis connection and cache management for Numerologist AI.

This module provides Redis connectivity with connection pooling for:
- Session/token storage
- Cache layer for expensive operations
- Rate limiting counters
- Real-time data (conversation state)

Configuration is centralized in src.core.settings.
"""

from typing import Any, Optional

import redis
from redis import Redis
from redis.connection import ConnectionPool

from .settings import settings


# Create Redis connection pool
# Configuration loaded from settings (environment variables or .env file)
redis_pool: Optional[ConnectionPool] = None
redis_client: Optional[Redis] = None


def get_redis_pool() -> ConnectionPool:
    """
    Get or create Redis connection pool.

    Uses singleton pattern to ensure single pool instance for the application.

    Returns:
        ConnectionPool: Redis connection pool instance
    """
    global redis_pool

    if redis_pool is None:
        redis_pool = redis.ConnectionPool.from_url(
            settings.redis_url,
            max_connections=settings.redis_pool_size,
            socket_keepalive=settings.redis_socket_keepalive,
            decode_responses=True,  # Automatically decode responses to strings
        )

    return redis_pool


def get_redis_client() -> Redis:
    """
    Get or create Redis client instance.

    Uses singleton pattern to ensure single client instance for the application.
    Client shares connection pool for efficient resource usage.

    Returns:
        Redis: Redis client instance

    Example:
        client = get_redis_client()
        client.set("key", "value")
        value = client.get("key")
    """
    global redis_client

    if redis_client is None:
        redis_client = redis.Redis(connection_pool=get_redis_pool())

    return redis_client


async def redis_health_check() -> dict:
    """
    Check Redis connection and return health status.

    Used for /health endpoint to verify Redis connectivity.

    Returns:
        dict: Health status with 'redis' key containing connection status

    Example:
        health = await redis_health_check()
        # Returns: {"redis": "connected"} or {"redis": "disconnected"}
    """
    try:
        client = get_redis_client()
        client.ping()
        return {"redis": "connected"}
    except Exception as e:
        import logging

        logging.error(f"Redis health check failed: {str(e)}")
        return {"redis": "disconnected", "error": str(e)}


def dispose_redis_pool() -> None:
    """
    Dispose of Redis connection pool.

    Should be called during application shutdown to properly close
    all connections in the pool.

    Called from application lifespan context manager on shutdown.
    """
    global redis_pool, redis_client

    if redis_client is not None:
        redis_client.close()
        redis_client = None

    if redis_pool is not None:
        redis_pool.disconnect()
        redis_pool = None


__all__ = [
    "get_redis_pool",
    "get_redis_client",
    "redis_health_check",
    "dispose_redis_pool",
]
