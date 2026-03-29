"""自定义分页类"""
from rest_framework.pagination import PageNumberPagination


class StandardPagination(PageNumberPagination):
    """支持动态 page_size 的标准分页类"""
    page_size = 20
    page_size_query_param = 'page_size'
    # 收紧全局上限，避免 page_size=9999 造成慢请求与大响应体。
    max_page_size = 1000
