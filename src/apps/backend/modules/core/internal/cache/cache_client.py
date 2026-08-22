import os
import threading
from typing import Optional

from redis import Redis

from modules.core.config.config_service import ConfigService


class CacheClient:
    _client: Optional[Redis] = None
    _owner_pid: Optional[int] = None
    _lock = threading.Lock()

    @classmethod
    def get_client(cls) -> Redis:
        current_pid = os.getpid()

        with cls._lock:
            client = cls._client
            if client is None or cls._owner_pid != current_pid:
                client = cls._replace_client(current_pid)
            return client

    @classmethod
    def reset(cls) -> None:
        with cls._lock:
            if cls._client is not None and cls._owner_pid == os.getpid():
                cls._client.close()
            cls._client = None
            cls._owner_pid = None

    @classmethod
    def _replace_client(cls, current_pid: int) -> Redis:
        # A pool inherited across a fork is abandoned, never closed: its sockets still belong to the parent.
        client = Redis.from_url(cls._connection_url(), decode_responses=True)
        cls._client = client
        cls._owner_pid = current_pid
        return client

    @staticmethod
    def _connection_url() -> str:
        return ConfigService[str].get_value(key="celery.broker_url")
