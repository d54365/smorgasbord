from base.constants.cache import CacheConstants
from ..env import PROJECT_DIR
from ..env import env

CACHES = {
    "default": {
        "BACKEND": "base.cache.RedisClusterClient",
        "LOCATION": env.str("DEFAULT_REDIS_URL"),
        "TIMEOUT": 300,
    },
    CacheConstants.CACHE_DISK_STR: {
        "BACKEND": "base.cache.DiskCacheClient",
        "LOCATION": f"{PROJECT_DIR}/_disk_cache",
        "TIMEOUT": 300,
        # ^-- Django setting for default timeout of each key.
        "SHARDS": 8,
        "DATABASE_TIMEOUT": 0.010,  # 10 milliseconds
        # ^-- Timeout for each DjangoCache database transaction.
        "OPTIONS": {"size_limit": 2**30},  # 1 gigabyte
    },
    CacheConstants.CACHE_LOCK_STR: {
        "BACKEND": "base.cache.RedisCacheClient",
        "LOCATION": env.str("LOCK_REDIS_URL"),
    },
}
