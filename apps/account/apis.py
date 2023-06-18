import time
import uuid

from django.conf import settings
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from base.auth.backends import JWTAuthentication
from base.constants.cache import CacheConstants
from base.exceptions.exception import ApplicationError
from base.oss import oss_client
from base.utils.header import HeaderUtil
from base.utils.random import Random
from user.models import User
from user.services import UserService
from .serializers import SMSInputSerializer, RegisterInputSerializer, TokenObtainPairSerializer, TokenRefreshSerializer
from .tasks import send_sms_code
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator


class AccountViewSet(viewsets.ViewSet):
    permission_classes = (permissions.AllowAny,)

    @action(methods=["POST"], detail=False, url_path="v1/sms_code")
    @method_decorator(ratelimit(key="post:mobile", rate="5/m"))
    @method_decorator(ratelimit(key="ip", rate="5/m"))
    def sms_code(self, request):
        serializer = SMSInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mobile = serializer.validated_data["mobile"]
        code = Random.generate_number(4)

        send_sms_code.delay(mobile, code)

        cache.set(
            CacheConstants.SMS_CODE.format(mobile=mobile), f"{code}_{int(time.time())}", CacheConstants.SMS_CODE_EXPIRED
        )
        return Response()

    @action(methods=["POST"], detail=False, url_path="v1/register")
    @method_decorator(ratelimit(key="ip", rate="3/s"))
    def register(self, request):
        serializer = RegisterInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data["code"]
        mobile = serializer.validated_data["mobile"]
        username = serializer.validated_data["username"]

        key = CacheConstants.SMS_CODE.format(mobile=mobile)
        if not cache.exists(key):  # noqa
            raise ApplicationError(message=_("验证码错误"))
        value = cache.get(key)
        if value.split("_")[0] != code:
            raise ApplicationError(message=_("验证码错误"))

        if UserService.check_username_exists(username):
            raise ApplicationError(message=_("用户名已注册"))
        if UserService.check_mobile_exists(mobile):
            raise ApplicationError(message=_("手机号码已注册"))

        cache.delete(key)

        UserService.create_user(serializer.validated_data, identity=User.Identity.USER)

        return Response(status=status.HTTP_201_CREATED)

    @action(methods=["POST"], detail=False, url_path="v1/login")
    @method_decorator(ratelimit(key="ip", rate="3/s"))
    def login(self, request):
        serializer = TokenObtainPairSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)

    @action(methods=["POST"], detail=False, url_path="v1/refresh_token")
    @method_decorator(ratelimit(key="ip", rate="3/h"))
    def refresh_token(self, request):
        serializer = TokenRefreshSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)

    @action(methods=["POST"], detail=False, url_path="v1/logout", authentication_classes=(JWTAuthentication,))
    @method_decorator(ratelimit(key="ip", rate="3/s"))
    def logout(self, request):
        ua_md5 = HeaderUtil.get_ua_md5(request)
        access_key = CacheConstants.USER_ACCESS_TOKEN.format(ua_md5=ua_md5, user_id=request.user.id)
        refresh_key = CacheConstants.USER_REFRESH_TOKEN.format(ua_md5=ua_md5, user_id=request.user.id)
        cache.delete(access_key)
        cache.delete(refresh_key)
        return Response()

    @action(methods=["POST"], detail=False, url_path="v1/upload_test")
    def upload_test(self, request):
        """单个文件直接上传"""
        file = request.FILES["file"]
        ret = oss_client.put_object(
            settings.MINIO_BUCKET,
            f"{uuid.uuid4().hex}.{file.name.split('.')[-1].lower()}",
            file,
            file.size,
            content_type=file.content_type,
        )
        print(ret.object_name)
        return Response()

    # 分片上传流程
    # 1. 前端上传文件, 计算文件大小, 5M一分片
    #   1.1 这里还可以根据前端传的文件md5来判断文件是否已经存在, 实现秒传功能
    # 2. 后台请求获取upload_id, 然后根据分片数量, 获取pre_url返回给前端, 前端用pre_url直接上传
    # 3. 前端上传完所有分片后, 再调用合并分片的接口
    @action(methods=["POST"], detail=False, url_path="v1/multipart/create")
    def multipart_create(self, request):
        """创建分片id"""
        file_name = request.data.get("file_name")
        chunk_count = request.data.get("chunk_count")
        object_name = f"{uuid.uuid4().hex}.{file_name.split('.')[-1].lower()}"
        upload_id = oss_client.create_multipart_upload(settings.MINIO_BUCKET, object_name)
        chunks = []
        for i in range(1, chunk_count + 1):
            chunks.append(
                {
                    "part_number": i - 1,
                    "upload_url": oss_client.presigned_put_object(
                        settings.MINIO_BUCKET, object_name, part_number=i, upload_id=upload_id
                    ),
                }
            )
        return Response({"upload_id": upload_id, "chunks": chunks, "object_name": object_name})

    @action(methods=["POST"], detail=False, url_path="v1/multipart/delete")
    def multipart_delete(self, request):
        """删除分片id"""
        upload_id = request.data.get("upload_id")
        object_name = request.data.get("object_name")
        oss_client.abort_multipart_upload(settings.MINIO_BUCKET, object_name, upload_id)
        return Response()

    @action(methods=["POST"], detail=False, url_path="v1/multipart/complete")
    def multipart_complete(self, request):
        """分片合并"""
        upload_id = request.data.get("upload_id")
        object_name = request.data.get("object_name")
        oss_client.complete_multipart_upload(settings.MINIO_BUCKET, object_name, upload_id)
        return Response()
