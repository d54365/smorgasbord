from .models import Inventory

# from django.db.models import F
from base.cache.redis.lock import Lock
from django.core.cache import caches
from base.constants.cache import CacheConstants
from base.exceptions.exception import ApplicationError
from django.utils.translation import gettext_lazy as _


class InventoryService:
    @staticmethod
    def deduct(pk, count):
        # 1. 通过mysql解决超卖问题
        # 但是如果商品库存存在于多个仓库, 需要根据业务逻辑来选择仓库扣减库存, 这种方式就不行了; 也没办法记录库存变化日志
        # Inventory.objects.filter(id=pk, quantity__gte=count).update(quantity=F("quantity") - count)

        # 2. 通过redis单节点分布式锁
        with Lock(
            caches[CacheConstants.CACHE_LOCK_STR].client,
            CacheConstants.INVENTORY_DEDUCT.format(id=pk),
            expire=CacheConstants.INVENTORY_DEDUCT_EXPIRED,
        ) as lock:  # noqa
            try:
                inventory = Inventory.objects.get(id=pk)
            except Inventory.DoesNotExist:
                raise ApplicationError(message=_("库存不存在"))
            if inventory.quantity < count:
                raise ApplicationError(message=_("库存不够"))
            inventory.quantity -= count
            inventory.save()
            # 其他操作

    @staticmethod
    def get_inventory_by_pk(pk):
        return Inventory.objects.get(id=pk)
