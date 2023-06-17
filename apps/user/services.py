from django.contrib.auth.hashers import make_password
from django.core.cache import cache

from base.constants.cache import CacheConstants
from .models import User


class UserService:
    @staticmethod
    def check_username_exists(username: str) -> bool:
        return User.objects.filter(is_delete=False, username=username).exists()

    @staticmethod
    def check_mobile_exists(mobile: str) -> bool:
        return User.objects.filter(is_delete=False, mobile=mobile).exists()

    @staticmethod
    def check_mail_exists(mail: str, instance: User = None) -> bool:
        queryset = User.objects.filter(is_delete=False, mail=mail)
        if instance is not None:
            queryset = queryset.exclude(id=instance.id)
        return queryset.exists()

    @staticmethod
    def create_user(user_info, identity: User.Identity, created: User = None) -> User:
        # 高并发下, 通过mysql的唯一索引保证username, mobile不会重复
        # 如果分库分表了, 则需要加分布式锁保证唯一性
        return User.objects.create(
            username=user_info["username"],
            password=make_password(user_info["password"]),
            mobile=user_info["mobile"],
            identity=identity,
            created=created,
        )

    @staticmethod
    def get_user_by_username(username: str) -> User:
        return User.objects.get(is_delete=False, username=username)

    @staticmethod
    def get_user_by_mobile(mobile: str) -> User:
        return User.objects.get(is_delete=False, mobile=mobile)

    @staticmethod
    def get_user_by_pk(pk: int) -> User:
        key = CacheConstants.USER_CACHE.format(user_id=pk)
        if cache.exists(key):  # noqa
            return cache.get(key)
        try:
            user_obj = User.objects.get(is_delete=False, id=pk)
        except User.DoesNotExist:
            user_obj = None
        if user_obj:
            cache.set(key, user_obj, CacheConstants.USER_CACHE_EXPIRED)
        return user_obj
