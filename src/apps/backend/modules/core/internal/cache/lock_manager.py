from typing import cast

from redis.exceptions import RedisError

from modules.core.internal.cache.cache_client import CacheClient
from modules.core.internal.cache.cache_manager import namespaced_key
from modules.logger.logger import Logger

RELEASE_IF_HELD_BY_TOKEN = """
if redis.call('get', KEYS[1]) == ARGV[1] then
    return redis.call('del', KEYS[1])
end
return 0
"""


class LockManager:
    @staticmethod
    def acquire(key: str, token: str, ttl_seconds: int) -> bool:
        key_in_store = namespaced_key(key)
        try:
            acquired = CacheClient.get_client().set(key_in_store, token, ex=ttl_seconds, nx=True)
        except (RedisError, OSError) as exc:
            Logger.warn(message=f"lock acquisition failed for {key_in_store}, running without the lock: {exc}")
            return True
        return bool(acquired)

    @staticmethod
    def release(key: str, token: str) -> bool:
        key_in_store = namespaced_key(key)
        try:
            deleted_count = CacheClient.get_client().eval(RELEASE_IF_HELD_BY_TOKEN, 1, key_in_store, token)
        except (RedisError, OSError) as exc:
            Logger.error(message=f"lock release failed for {key_in_store}, it expires on its own: {exc}")
            return False
        return cast(int, deleted_count) == 1
