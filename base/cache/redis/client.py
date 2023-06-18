from django.core.cache import BaseCache
from redis.cluster import RedisCluster
from redis.client import Redis

from base.cache.serializer import CacheSerializer

try:
    from django.core.cache.backends.base import DEFAULT_TIMEOUT
except ImportError:  # pragma: no cover
    # For older versions of Django simply use 300 seconds.
    DEFAULT_TIMEOUT = 300


class CommonOperation:
    _client = None
    _serializer = None
    default_timeout = None

    @property
    def client(self):
        return self._client

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
            if ret := bool(self._client.set(key, value, nx=True)):
                self._client.delete(key)
            return ret
        else:
            return bool(self._client.set(key, value, ex=timeout, nx=True))

    def get(self, key, default=None, version=None):
        value = self._client.get(key)
        return default if value is None else self._serializer.loads(value)

    def set(self, key, value, timeout=DEFAULT_TIMEOUT, version=None, px=None, nx=False, xx=False):
        value = self._serializer.dumps(value)
        timeout = self.get_backend_timeout(timeout)
        if timeout == 0:
            self._client.delete(key)
        else:
            self._client.set(key, value, ex=timeout, px=px, nx=nx, xx=xx)

    def touch(self, key, timeout=DEFAULT_TIMEOUT, version=None):
        timeout = self.get_backend_timeout(timeout)
        if timeout is None:
            return bool(self._client.persist(key))
        else:
            return bool(self._client.expire(key, timeout))

    def delete(self, key, version=None):
        return bool(self._client.delete(key))

    def clear(self):
        return bool(self._client.flushdb())

    def has_key(self, key, version=None):
        return bool(self._client.exists(key))

    def exists(self, *keys):
        return self._client.exists(*keys)

    def incr(self, key, delta=1, version=None):
        return self._client.incr(key, delta)

    def delete_many(self, keys, version=None):
        return self._client.delete(*keys)

    def setex(self, name, time, value):
        return self._client.setex(name, time, self._serializer.dumps(value))

    def expire(self, name, time, nx=False, xx=False, gt=False, lt=False):
        return self._client.expire(name, time, nx, xx, gt, lt)


class RedisClusterClient(CommonOperation, BaseCache):
    def __init__(self, url, *args):
        super().__init__(*args)
        self._serializer = CacheSerializer()
        self._client = RedisCluster.from_url(url)

    def set_many(self, data, timeout=DEFAULT_TIMEOUT, version=None):
        data = {k: self._serializer.dumps(v) for k, v in data.items()}
        return self._client.mset_nonatomic(data)


class RedisCacheClient(CommonOperation, BaseCache):
    def __init__(self, url, *args):
        super().__init__(*args)
        self._serializer = CacheSerializer()
        self._client = Redis.from_url(url)
