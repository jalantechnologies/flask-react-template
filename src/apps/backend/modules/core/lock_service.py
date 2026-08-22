from modules.core.internal.cache.lock_manager import LockManager


class LockService:
    @staticmethod
    def acquire(*, key: str, token: str, ttl_seconds: int) -> bool:
        return LockManager.acquire(key=key, token=token, ttl_seconds=ttl_seconds)

    @staticmethod
    def release(*, key: str, token: str) -> bool:
        return LockManager.release(key=key, token=token)
