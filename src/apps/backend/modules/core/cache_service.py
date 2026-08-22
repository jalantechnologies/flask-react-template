from typing import Optional

from modules.core.internal.cache.cache_manager import CacheManager


class CacheService:
    @staticmethod
    def get(*, key: str) -> Optional[str]:
        return CacheManager.get(key=key)

    @staticmethod
    def set(*, key: str, value: str, ttl_seconds: int) -> None:
        CacheManager.set(key=key, value=value, ttl_seconds=ttl_seconds)

    @staticmethod
    def discard(*, key: str) -> None:
        CacheManager.discard(key=key)
