from django.core.cache import cache


class ClearCacheMixin:
    """Mixin for clearing cache after every test"""

    def setUp(self) -> None:
        cache.clear()

    def tearDown(self) -> None:
        cache.clear()
