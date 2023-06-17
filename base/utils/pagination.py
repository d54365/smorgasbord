from rest_framework.pagination import LimitOffsetPagination as LimitOffsetPagination_
from rest_framework.pagination import PageNumberPagination as PageNumberPagination_


class LimitOffsetPagination(LimitOffsetPagination_):
    max_limit = 100  # 最大每页显示条数
    default_limit = 20  # 默认每页显示多少条
    limit_query_param = "limit"
    offset_query_param = "offset"


class PageNumberPagination(PageNumberPagination_):
    max_page_size = 100  # 最大每页显示条数
    page_size = 20  # 默认每页显示多少条
    page_size_query_param = "size"
    page_query_param = "page"
