import re

from django.contrib.auth.backends import ModelBackend
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _
from rest_framework import HTTP_HEADER_ENCODING
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication as JWTAuthentication_
from rest_framework_simplejwt.settings import api_settings

from base.constants.cache import CacheConstants
from base.constants.re import ReConstants
from base.utils.header import HeaderUtil
from user.models import User
from user.services import UserService


class UsernameOrMobileBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            if re.match(ReConstants.MOBILE_PATTERN, username):
                user = UserService.get_user_by_mobile(username)
            else:
                user = UserService.get_user_by_username(username)
        except User.DoesNotExist:
            return None

        if not user.check_password(password):
            return None

        return user


class BaseJWTAuthentication(JWTAuthentication_):
    www_authenticate_realm = "api"

    def authenticate(self, request):
        user_id, validated_token = self.get_user_id_and_token(request)

        key = CacheConstants.USER_ACCESS_TOKEN.format(ua_md5=HeaderUtil.get_ua_md5(request), user_id=user_id)

        if cache.get(key) != str(validated_token):
            raise AuthenticationFailed(_("Token is expired"))

        return self.get_user(validated_token), validated_token

    def get_user_id_and_token(self, request):
        header = self.get_header(request)
        if header is None:
            raise AuthenticationFailed(_("Can not get token from header"))

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            raise AuthenticationFailed(_("Can not get token from header"))

        validated_token = self.get_validated_token(raw_token)

        try:
            user_id = validated_token[api_settings.USER_ID_CLAIM]
        except KeyError:
            raise AuthenticationFailed(_("Token contained no recognizable user identification"))

        return user_id, validated_token

    def get_raw_token(self, header):
        """
        Extracts an unvalidated JSON web token from the given "Authorization"
        header value.
        """
        parts = header.split()

        if len(parts) == 0:
            # Empty AUTHORIZATION header sent
            return None

        if parts[0] not in self.AUTH_HEADER_TYPE_BYTES:  # noqa
            # Assume the header does not contain a JSON web token
            return None

        if len(parts) != 2:
            raise AuthenticationFailed(_("Authorization header must contain two space-delimited values"))

        return parts[1]


class JWTAuthentication(BaseJWTAuthentication):
    www_authenticate_realm = "api"
    AUTH_HEADER_TYPE_BYTES = {h.encode(HTTP_HEADER_ENCODING) for h in ("Bearer",)}

    def get_user(self, validated_token):
        user_id = validated_token[api_settings.USER_ID_CLAIM]

        user = UserService.get_user_by_pk(user_id)
        if not user:
            raise AuthenticationFailed(_("User not found"))

        if not user.is_active:
            raise AuthenticationFailed(_("User is disabled"))

        return user
