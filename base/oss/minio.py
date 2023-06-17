from datetime import timedelta

from loguru import logger
from minio import Minio
from minio.deleteobjects import DeleteObject
from minio.helpers import genheaders, ObjectWriteResult
from urllib3.exceptions import ResponseError

from .base import OssBase


class MinIOOss(OssBase):
    def __init__(self, host, access_key, secret_key, secure=True):
        self._client = Minio(host, access_key, secret_key, secure=secure)

    def get_object(self, bucket, object_name, offset=0, length=0, request_headers=None):
        local = locals()
        del local["self"]

        try:
            return self._client.get_object(bucket, object_name, offset, length, request_headers=request_headers)
        except ResponseError as e:
            logger.error({"type": "OSS get_object", "error": e, **local})

    def fget_object(self, bucket, object_name, file_path, request_headers=None):
        local = locals()
        del local["self"]

        try:
            return self._client.fget_object(bucket, object_name, file_path, request_headers)
        except ResponseError as e:
            logger.error({"type": "OSS fget_object", "error": e, **local})

    def copy_object(
        self,
        bucket,
        object_name,
        source,
        sse=None,
        metadata=None,
        tags=None,
        retention=None,
        legal_hold=False,
        metadata_directive=None,
        tagging_directive=None,
    ):
        local = locals()
        del local["self"]

        try:
            return self._client.copy_object(
                bucket,
                object_name,
                source,
                sse,
                metadata,
                tags,
                retention,
                legal_hold,
                metadata_directive,
                tagging_directive,
            )
        except Exception as e:
            logger.error({"type": "OSS copy_object", "error": e, **local})

    def put_object(
        self,
        bucket,
        object_name,
        data,
        length,
        content_type="application/octet-stream",
        metadata=None,
        sse=None,
        progress=None,
        part_size=0,
        num_parallel_uploads=3,
        tags=None,
        retention=None,
        legal_hold=False,
    ):
        local = locals()
        del local["self"]

        try:
            return self._client.put_object(
                bucket,
                object_name,
                data,
                length,
                content_type,
                metadata,
                sse,
                progress,
                part_size,
                num_parallel_uploads,
                tags,
                retention,
                legal_hold,
            )
        except Exception as e:
            logger.error({"type": "OSS put_object", "error": e, **local})

    def fput_object(
        self,
        bucket,
        object_name,
        file_path,
        content_type="application/octet-stream",
        metadata=None,
        sse=None,
        progress=None,
        part_size=0,
        num_parallel_uploads=3,
        tags=None,
        retention=None,
        legal_hold=False,
    ):
        local = locals()
        del local["self"]

        try:
            return self._client.fput_object(
                bucket,
                object_name,
                file_path,
                content_type,
                metadata,
                sse,
                progress,
                part_size,
                num_parallel_uploads,
                tags,
                retention,
            )
        except ResponseError as e:
            logger.error({"type": "OSS fput_object", "error": e, **local})

    def remove_object(self, bucket, object_name, version_id=None):
        local = locals()
        del local["self"]

        try:
            self._client.remove_object(bucket, object_name, version_id)
        except ResponseError as e:
            logger.error({"type": "OSS remove_object", "error": e, **local})

    def remove_objects(self, bucket, object_names, bypass_governance_mode=False):
        local = locals()
        del local["self"]

        delete_object_list = [DeleteObject(object_name) for object_name in object_names]

        try:
            errors = self._client.remove_objects(bucket, delete_object_list)
            return errors
        except ResponseError as e:
            logger.error({"type": "OSS remove_objects", "error": e, **local})

    def presigned_get_object(
        self,
        bucket,
        object_name,
        expires=timedelta(days=7),
        response_headers=None,
        request_date=None,
        version_id=None,
        extra_query_params=None,
    ):
        return self._client.presigned_get_object(
            bucket, object_name, expires, response_headers, request_date, version_id, extra_query_params
        )

    def presigned_put_object(self, bucket, object_name, expires=timedelta(hours=1), part_number=None, upload_id=None):
        extra_query_params = None
        if part_number and upload_id:
            extra_query_params = {
                "partNumber": str(part_number),
                "uploadId": upload_id,
            }
        return self._client.get_presigned_url(
            "PUT", bucket, object_name, expires=expires, extra_query_params=extra_query_params
        )

    def create_multipart_upload(
        self,
        bucket_name,
        object_name,
        content_type="application/octet-stream",
        metadata=None,
        sse=None,
        tags=None,
        retention=None,
        legal_hold=False,
    ):
        headers = genheaders(metadata, sse, tags, retention, legal_hold)
        headers["Content-Type"] = content_type
        upload_id = self._client._create_multipart_upload(bucket_name, object_name, headers)  # noqa
        return upload_id

    def abort_multipart_upload(self, bucket_name, object_name, upload_id):
        self._abort_multipart_upload(bucket_name, object_name, upload_id)  # noqa

    def complete_multipart_upload(self, bucket, object_name, upload_id):
        local = locals()
        del local["self"]

        parts = self._client._list_parts(bucket, object_name, upload_id, part_number_marker=0).parts  # noqa

        try:
            result = self._client._complete_multipart_upload(bucket, object_name, upload_id, parts)  # noqa
        except Exception as e:
            logger.error({"type": "OSS complete_multipart_upload", "error": e, **local})
            return None
        return ObjectWriteResult(
            result.bucket_name,
            result.object_name,
            result.version_id,
            result.etag,
            result.http_headers,
            location=result.location,
        )
