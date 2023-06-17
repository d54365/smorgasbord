import time

from django.conf import settings
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _
from itsdangerous import URLSafeSerializer, BadData
from rest_framework import serializers

from base.constants.cache import CacheConstants
from base.exceptions.exception import ApplicationError
from user.models import User
from user.services import UserService


class UserCenterOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "mobile", "mail", "mail_active", "identity")


class SendMailInputSerializer(serializers.Serializer):
    mail = serializers.EmailField()

    def validate(self, attrs):
        if UserService.check_mail_exists(attrs["mail"], self.instance):
            raise ApplicationError(message=_("邮箱已被使用"))

        if self.instance.mail == attrs["mail"] and self.instance.mail_active:
            raise ApplicationError(message=_("该邮箱已激活"))
        key = CacheConstants.EMAIL_ACTIVE.format(user_id=self.instance.id)
        if cache.exists(key):
            value = cache.get(key)
            if time.time() - int(value.split("_")[1]) < 60:
                raise ApplicationError(message=_("60秒内不能重复发送"))

        # 避免24小时内容发送多次
        limit_key = CacheConstants.EMAIL_ACTIVE_LIMIT.format(user_id=self.instance.id)
        if cache.get(limit_key):
            value = cache.get(limit_key)
            if value > 5:
                raise ApplicationError(message=_("24小时内只能发送5次"))

        return attrs


class ActivateMailInputSerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate(self, attrs):
        url_safe_serializer = URLSafeSerializer(settings.SECRET_KEY)
        try:
            payload = url_safe_serializer.loads(attrs["token"])
        except BadData:
            raise ApplicationError(message="激活邮件已过期", extra={"errmsg": "token解析失败"})

        user_id = payload.get("user_id")
        mail = payload.get("mail")
        if not user_id or not mail:
            raise ApplicationError(message="激活邮件已过期", extra={"errmsg": "缺少元数据"})

        key = CacheConstants.EMAIL_ACTIVE.format(user_id=user_id)
        value = cache.get(key)
        if value.split("_")[0] != attrs["token"]:
            raise ApplicationError(message="激活邮件已过期")

        user = UserService.get_user_by_pk(user_id)
        if not user:
            raise ApplicationError(message="激活邮件已过期", extra={"errmsg": "用户已被删除"})

        if user.mail != mail:
            raise ApplicationError(message="激活邮件已过期", extra={"errmsg": "邮箱已修改"})

        attrs["payload"] = payload
        attrs["user"] = user
        attrs["key"] = key
        return attrs
