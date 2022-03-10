from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination


class DefaultLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 15


class DefaultPageNumberPagination(PageNumberPagination):
    page_size = 15
