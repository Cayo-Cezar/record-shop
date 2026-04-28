import redis
import json
import hashlib
from typing import Any, Optional
from app.core.config import settings

# Connection pool shared across all coroutines / threads
# ssl_cert_reqs="none" is required for Upstash (rediss://) on cloud environments
_pool = redis.ConnectionPool.from_url(
    settings.REDIS_URL,
    max_connections=50,
    decode_responses=True,
    ssl_cert_reqs="none" if settings.REDIS_URL.startswith("rediss://") else None,
)


def get_redis() -> redis.Redis:
    """Return a Redis client backed by the shared connection pool."""
    return redis.Redis(connection_pool=_pool)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_list_cache_key(prefix: str, **filters: Any) -> str:
    """Deterministic cache key from a dict of filter parameters."""
    raw = json.dumps(filters, sort_keys=True, default=str)
    digest = hashlib.md5(raw.encode()).hexdigest()
    return f"{prefix}:{digest}"


def cache_get(key: str) -> Optional[Any]:
    r = get_redis()
    raw = r.get(key)
    return json.loads(raw) if raw else None


def cache_set(key: str, value: Any, ttl: int) -> None:
    r = get_redis()
    r.setex(key, ttl, json.dumps(value, default=str))


def cache_delete(key: str) -> None:
    r = get_redis()
    r.delete(key)


def cache_delete_pattern(pattern: str) -> None:
    """Delete all keys matching a glob pattern (use carefully in prod)."""
    r = get_redis()
    cursor = 0
    while True:
        cursor, keys = r.scan(cursor, match=pattern, count=100)
        if keys:
            r.delete(*keys)
        if cursor == 0:
            break
