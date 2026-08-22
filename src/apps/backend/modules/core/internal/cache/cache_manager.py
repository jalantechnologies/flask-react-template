from typing import Optional, cast

from redis.exceptions import RedisError

from modules.config.config_service import ConfigService
from modules.core.errors import CacheDiscardFailedError, CacheNonPositiveTTLError
from modules.core.internal.cache.cache_client import CacheClient
from modules.logger.logger import Logger

DEFAULT_KEY_PREFIX = "flask-react-template"
KEY_PREFIX_SEPARATOR = ":"


class CacheManager:
    @staticmethod
    def get(key: str) -> Optional[str]:
        namespaced_key = CacheManager._namespaced(key)
        try:
            value = CacheClient.get_client().get(namespaced_key)
        except (RedisError, OSError) as exc:
            Logger.warn(message=f"cache read failed for {namespaced_key}, treating as a miss: {exc}")
            return None
        return cast(Optional[str], value)

    @staticmethod
    def set(key: str, value: str, ttl_seconds: int) -> None:
        if ttl_seconds <= 0:
            raise CacheNonPositiveTTLError(ttl_seconds=ttl_seconds)

        namespaced_key = CacheManager._namespaced(key)
        try:
            CacheClient.get_client().set(namespaced_key, value, ex=ttl_seconds)
        except (RedisError, OSError) as exc:
            Logger.warn(message=f"cache write failed for {namespaced_key}, entry not stored: {exc}")

    @staticmethod
    def discard(key: str) -> None:
        namespaced_key = CacheManager._namespaced(key)
        try:
            CacheClient.get_client().delete(namespaced_key)
        except (RedisError, OSError) as exc:
            Logger.error(message=f"cache invalidation failed for {namespaced_key}: {exc}")
            raise CacheDiscardFailedError(key=namespaced_key, reason=str(exc)) from exc

    @staticmethod
    def _namespaced(key: str) -> str:
        prefix = ConfigService[str].get_value(key="cache.key_prefix", default=DEFAULT_KEY_PREFIX)
        return f"{prefix}{KEY_PREFIX_SEPARATOR}{key}"
