from abc import ABC, abstractmethod


class OssBase(ABC):
    @abstractmethod
    def get_object(self, bucket, object_name, offset=0, length=0, request_headers=None):
        ...

    @abstractmethod
    def fget_object(self, bucket, object_name, file_path, request_headers=None):
        ...

    @abstractmethod
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
        ...

    @abstractmethod
    def put_object(
        self,
        bucket,
        object_name,
        data,
        length,
        content_type=None,
        metadata=None,
        sse=None,
        progress=None,
        part_size=0,
        num_parallel_uploads=3,
        tags=None,
        retention=None,
        legal_hold=False,
    ):
        ...

    @abstractmethod
    def fput_object(
        self,
        bucket,
        object_name,
        file_path,
        content_type,
        metadata=None,
        sse=None,
        progress=None,
        part_size=0,
        num_parallel_uploads=3,
        tags=None,
        retention=None,
        legal_hold=False,
    ):
        ...

    @abstractmethod
    def remove_object(self, bucket, object_name, version_id=None):
        ...

    @abstractmethod
    def remove_objects(self, bucket, object_names, bypass_governance_mode=False):
        ...

    @abstractmethod
    def presigned_get_object(
        self,
        bucket,
        object_name,
        expires,
        response_headers=None,
        request_date=None,
        version_id=None,
        extra_query_params=None,
    ):
        ...

    @staticmethod
    def presigned_put_object(self, bucket, object_name, expires):
        ...
