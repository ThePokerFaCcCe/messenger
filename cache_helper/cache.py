from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.conf import settings

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)


class Cache:
    """
    Cache helper class that has a pattern for keys.
    """
    key_patterns = None

    def __init__(self) -> None:
        assert self.key_patterns is not None, (
            f"`key_patterns` attr must set in {self.__class__.__name__}"
        )

    @property
    def _cache(self):
        """Return real cache object"""
        return cache

    def format_key(self, *format_args, key_name: str = None, **format_kwargs) -> str:
        """Return formatted key"""
        patterns = self.key_patterns
        pattern = None

        if key_name == None:
            if isinstance(patterns, str):
                pattern = patterns
            else:
                pattern = patterns.get('default')
                assert pattern is not None, (
                    "'default' key must set or a `key_name` must be passed")
        else:
            pattern = patterns[key_name]

        return pattern.format(*format_args, **format_kwargs)

    def set(self, key: str, value, timeout: int = CACHE_TTL):
        return cache.set(key, value, timeout=timeout)

    def get(self, key: str, default=None):
        if key not in cache:
            return default
        return cache.get(key)

    def delete(self, key):
        return cache.delete(key)
