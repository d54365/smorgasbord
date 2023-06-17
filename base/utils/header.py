from hashlib import md5

from django.core.cache import caches, cache
from rest_framework.request import Request

from base.constants.cache import CacheConstants


class HeaderUtil:
    @staticmethod
    def get_ua(request: Request):
        return request.META.get("HTTP_USER_AGENT", "")

    @classmethod
    def get_ua_md5(cls, request):
        ua = cls.get_ua(request)
        key = CacheConstants.USER_AGENT.format(ua=ua)
        disk_cache = caches[CacheConstants.CACHE_DISK_STR]
        if disk_cache.has_key(key):  # noqa
            return disk_cache.get(key)
        if cache.exists(key):  # noqa
            return cache.get(key)
        ua_md5 = md5(ua.encode("utf-8")).hexdigest()
        disk_cache.set(key, ua_md5, timeout=None)
        cache.set(key, ua_md5)
        return ua_md5

    @staticmethod
    def get_client_ip(request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip
