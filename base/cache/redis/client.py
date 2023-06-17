from django.core.cache import BaseCache
from redis.cluster import RedisCluster

from base.cache.serializer import CacheSerializer

try:
    from django.core.cache.backends.base import DEFAULT_TIMEOUT
except ImportError:  # pragma: no cover
    # For older versions of Django simply use 300 seconds.
    DEFAULT_TIMEOUT = 300


class RedisClusterClient(BaseCache):
    def __init__(self, url, *args):
        super().__init__(*args)
        self._serializer = CacheSerializer()
        self._cache = RedisCluster.from_url(url)

    @property
    def cache(self):
        return self._cache

    def get_backend_timeout(self, timeout=DEFAULT_TIMEOUT):
        if timeout == DEFAULT_TIMEOUT:
            timeout = self.default_timeout
            # The key will be made persistent if None used as a timeout.
            # Non-positive values will cause the key to be deleted.
        return timeout

    def add(self, key, value, timeout=DEFAULT_TIMEOUT, version=None):
        value = self._serializer.dumps(value)
        timeout = self.get_backend_timeout(timeout)
        if timeout == 0:
            if ret := bool(self._cache.set(key, value, nx=True)):
                self._cache.delete(key)
            return ret
        else:
            return bool(self._cache.set(key, value, ex=timeout, nx=True))

    def get(self, key, default=None, version=None):
        value = self._cache.get(key)
        return default if value is None else self._serializer.loads(value)

    def set(self, key, value, timeout=DEFAULT_TIMEOUT, version=None):
        value = self._serializer.dumps(value)
        timeout = self.get_backend_timeout(timeout)
        if timeout == 0:
            self._cache.delete(key)
        else:
            self._cache.set(key, value, ex=timeout)

    def touch(self, key, timeout=DEFAULT_TIMEOUT, version=None):
        timeout = self.get_backend_timeout(timeout)
        if timeout is None:
            return bool(self._cache.persist(key))
        else:
            return bool(self._cache.expire(key, timeout))

    def delete(self, key, version=None):
        return bool(self._cache.delete(key))

    def clear(self):
        return bool(self._cache.flushdb())

    def has_key(self, key, version=None):
        return bool(self._cache.exists(key))

    def exists(self, *keys):
        return self._cache.exists(*keys)

    def incr(self, key, delta=1, version=None):
        return self._cache.incr(key, delta)

    def set_many(self, data, timeout=DEFAULT_TIMEOUT, version=None):
        data = {k: self._serializer.dumps(v) for k, v in data.items()}
        return self._cache.mset_nonatomic(data)

    def delete_many(self, keys, version=None):
        return self._cache.delete(*keys)

    def setex(self, name, time, value):
        return self._cache.setex(name, time, self._serializer.dumps(value))

    def expire(self, name, time, nx=False, xx=False, gt=False, lt=False):
        return self._cache.expire(name, time, nx, xx, gt, lt)
