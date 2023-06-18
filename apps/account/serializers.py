import time

from django.contrib.auth import authenticate
from django.core.cache import cache
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework_simplejwt.exceptions import TokenError, AuthenticationFailed
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer as TokenObtainPairSerializer_,
    TokenRefreshSerializer as TokenRefreshSerializer_,
)
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken

from base.constants.cache import CacheConstants
from base.constants.re import ReConstants
from base.exceptions.exception import ApplicationError
from base.utils.header import HeaderUtil
from user.services import UserService


class RegisterInputSerializer(serializers.Serializer):
    username = serializers.RegexField(regex=ReConstants.USERNAME_PATTERN)
    password = serializers.RegexField(regex=ReConstants.PASSWORD_PATTERN)
    mobile = serializers.RegexField(regex=ReConstants.MOBILE_PATTERN)
    code = serializers.CharField(min_length=4, max_length=4)


class SMSInputSerializer(serializers.Serializer):
    TYPE_LOGIN = 0
    TYPE_REGISTER = 1
    TYPE_CHOICES = ((TYPE_LOGIN, "登陆"), (TYPE_REGISTER, "注册"))

    mobile = serializers.RegexField(regex=ReConstants.MOBILE_PATTERN)
    type = serializers.ChoiceField(choices=TYPE_CHOICES)

    def validate(self, attrs):
        mobile = attrs["mobile"]

        sms_code_key = CacheConstants.SMS_CODE.format(mobile=mobile)
        if cache.exists(sms_code_key):  # noqa
            value = cache.get(sms_code_key)
            send_time = int(value.split("_")[1])
            if int(time.time()) - send_time < 60:
                raise ApplicationError(message=_("60秒内不能重复发送"))

        if attrs["mobile"] == self.TYPE_LOGIN:
            if not UserService.check_mobile_exists(mobile):
                raise ApplicationError(message=_("该手机号码未注册"))
        else:
            if UserService.check_mobile_exists(mobile):
                raise ApplicationError(message=_("该手机号码已注册"))

        return attrs


class TokenObtainPairSerializer(TokenObtainPairSerializer_):
    token_class = RefreshToken

    def validate(self, attrs):
        request = self.context["request"]

        authenticate_kwargs = {
            self.username_field: attrs[self.username_field],
            "password": attrs["password"],
            "request": request,
        }

        user = authenticate(**authenticate_kwargs)

        if user is None:
            raise ApplicationError(message=_("用户名或密码错误"))

        if not user.is_active:
            raise ApplicationError(message=_("用户处于禁用状态"))

        refresh = self.get_token(user)
        data = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "access_expired": int(api_settings.ACCESS_TOKEN_LIFETIME.total_seconds()),
            "refresh_expired": int(api_settings.REFRESH_TOKEN_LIFETIME.total_seconds()),
            "user_id": user.id,
            "username": user.username,  # noqa
            "mobile": user.mobile,  # noqa
            "mail": user.mail,  # noqa
            "identity": user.identity,  # noqa
            "type": api_settings.AUTH_HEADER_TYPES,
        }

        user.last_login_at = timezone.now()
        user.save()

        ua_md5 = HeaderUtil.get_ua_md5(request)
        access_key = CacheConstants.USER_ACCESS_TOKEN.format(ua_md5=ua_md5, user_id=user.id)
        refresh_key = CacheConstants.USER_REFRESH_TOKEN.format(ua_md5=ua_md5, user_id=user.id)
        cache.set(access_key, data["access"], api_settings.ACCESS_TOKEN_LIFETIME)
        cache.set(refresh_key, data["refresh"], api_settings.REFRESH_TOKEN_LIFETIME)
        return data


class TokenRefreshSerializer(TokenRefreshSerializer_):
    token_class = RefreshToken

    def validate(self, attrs):
        request = self.context["request"]

        try:
            user_id = self.token_class(attrs["refresh"])[api_settings.USER_ID_CLAIM]
        except TokenError:
            raise AuthenticationFailed("token decode error")

        ua_md5 = HeaderUtil.get_ua_md5(request)
        refresh_key = CacheConstants.USER_REFRESH_TOKEN.format(ua_md5=ua_md5, user_id=user_id)
        if cache.get(refresh_key) != attrs["refresh"]:
            raise AuthenticationFailed(_("refresh token is expired"))

        attrs = super().validate(attrs)

        access_key = CacheConstants.USER_ACCESS_TOKEN.format(ua_md5=ua_md5, user_id=user_id)
        cache.set(access_key, attrs["access"], api_settings.ACCESS_TOKEN_LIFETIME)

        return attrs
