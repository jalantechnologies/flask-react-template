from typing import Optional, cast

from redis.exceptions import RedisError

from modules.config.config_service import ConfigService
from modules.core.errors import CacheDiscardFailedError, CacheNonPositiveTTLError
from modules.core.internal.cache.cache_client import CacheClient
from modules.logger.logger import Logger

DEFAULT_KEY_PREFIX = "flask-react-template"
KEY_PREFIX_SEPARATOR = ":"


def namespaced_key(key: str) -> str:
    prefix = ConfigService[str].get_value(key="cache.key_prefix", default=DEFAULT_KEY_PREFIX)
    return f"{prefix}{KEY_PREFIX_SEPARATOR}{key}"


class CacheManager:
    @staticmethod
    def get(key: str) -> Optional[str]:
        key_in_store = namespaced_key(key)
        try:
            value = CacheClient.get_client().get(key_in_store)
        except (RedisError, OSError) as exc:
            Logger.warn(message=f"cache read failed for {key_in_store}, treating as a miss: {exc}")
            return None
        return cast(Optional[str], value)

    @staticmethod
    def set(key: str, value: str, ttl_seconds: int) -> None:
        if ttl_seconds <= 0:
            raise CacheNonPositiveTTLError(ttl_seconds=ttl_seconds)

        key_in_store = namespaced_key(key)
        try:
            CacheClient.get_client().set(key_in_store, value, ex=ttl_seconds)
        except (RedisError, OSError) as exc:
            Logger.warn(message=f"cache write failed for {key_in_store}, entry not stored: {exc}")

    @staticmethod
    def discard(key: str) -> None:
        key_in_store = namespaced_key(key)
        try:
            CacheClient.get_client().delete(key_in_store)
        except (RedisError, OSError) as exc:
            Logger.error(message=f"cache invalidation failed for {key_in_store}: {exc}")
            raise CacheDiscardFailedError(key=key_in_store, reason=str(exc)) from exc
