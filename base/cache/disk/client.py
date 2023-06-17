from diskcache import DjangoCache

from base.cache.serializer import CacheSerializer

try:
    from django.core.cache.backends.base import DEFAULT_TIMEOUT
except ImportError:  # pragma: no cover
    # For older versions of Django simply use 300 seconds.
    DEFAULT_TIMEOUT = 300


class DiskCacheClient(DjangoCache):
    def __init__(self, directory, params):
        """Initialize DjangoCache instance.

        :param str directory: cache directory
        :param dict params: cache parameters

        """
        super().__init__(directory, params)
        self._serializer = CacheSerializer()

    def add(
        self,
        key,
        value,
        timeout=DEFAULT_TIMEOUT,
        version=None,
        read=False,
        tag=None,
        retry=True,
    ):
        """Set a value in the cache if the key does not already exist. If
        timeout is given, that timeout will be used for the key; otherwise the
        default cache timeout will be used.

        Return True if the value was stored, False otherwise.

        :param key: key for item
        :param value: value for item
        :param float timeout: seconds until the item expires
            (default 300 seconds)
        :param int version: key version number (default None, cache parameter)
        :param bool read: read value as bytes from file (default False)
        :param str tag: text to associate with key (default None)
        :param bool retry: retry if database timeout occurs (default True)
        :return: True if item was added

        """
        value = self._serializer.dumps(value)
        return super().add(key, value, timeout, version, read, tag, retry)

    def get(
        self,
        key,
        default=None,
        version=None,
        read=False,
        expire_time=False,
        tag=False,
        retry=False,
    ):
        """Fetch a given key from the cache. If the key does not exist, return
        default, which itself defaults to None.

        :param key: key for item
        :param default: return value if key is missing (default None)
        :param int version: key version number (default None, cache parameter)
        :param bool read: if True, return file handle to value
            (default False)
        :param float expire_time: if True, return expire_time in tuple
            (default False)
        :param tag: if True, return tag in tuple (default False)
        :param bool retry: retry if database timeout occurs (default False)
        :return: value for item if key is found else default

        """
        key = self.make_key(key, version=version)
        value = self._cache.get(key, None, read, expire_time, tag, retry)
        return default if value is None else self._serializer.loads(value)

    def set(
        self,
        key,
        value,
        timeout=DEFAULT_TIMEOUT,
        version=None,
        read=False,
        tag=None,
        retry=True,
    ):
        """Set a value in the cache. If timeout is given, that timeout will be
        used for the key; otherwise the default cache timeout will be used.

        :param key: key for item
        :param value: value for item
        :param float timeout: seconds until the item expires
            (default 300 seconds)
        :param int version: key version number (default None, cache parameter)
        :param bool read: read value as bytes from file (default False)
        :param str tag: text to associate with key (default None)
        :param bool retry: retry if database timeout occurs (default True)
        :return: True if item was set

        """
        value = self._serializer.dumps(value)
        return super().set(key, value, timeout, version, read, tag, retry)

    def pop(
        self,
        key,
        default=None,
        version=None,
        expire_time=False,
        tag=False,
        retry=True,
    ):
        """Remove corresponding item for `key` from cache and return value.

        If `key` is missing, return `default`.

        Operation is atomic. Concurrent operations will be serialized.

        :param key: key for item
        :param default: return value if key is missing (default None)
        :param int version: key version number (default None, cache parameter)
        :param float expire_time: if True, return expire_time in tuple
            (default False)
        :param tag: if True, return tag in tuple (default False)
        :param bool retry: retry if database timeout occurs (default True)
        :return: value for item if key is found else default

        """
        key = self.make_key(key, version=version)
        value = self._cache.pop(key, None, expire_time, tag, retry)
        return default if value is None else self._serializer.loads(value)
