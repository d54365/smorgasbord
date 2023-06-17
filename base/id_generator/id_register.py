from django.core.cache import cache

from base.constants.cache import CacheConstants


class Register:
    @staticmethod
    def get_worker_id(max_worker_id=1023):
        return (cache.incr(CacheConstants.ID_GEN)) % max_worker_id
