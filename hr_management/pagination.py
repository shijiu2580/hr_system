"""自定义分页类"""
from rest_framework.pagination import PageNumberPagination


class StandardPagination(PageNumberPagination):
    """支持动态 page_size 的标准分页类"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 10000
