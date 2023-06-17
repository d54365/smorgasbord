from django.conf import settings

from .minio import MinIOOss

oss_client = MinIOOss(settings.MINIO_HOST, settings.MINIO_ACCESS_KEY, settings.MINIO_SECRET_KEY, secure=False)
