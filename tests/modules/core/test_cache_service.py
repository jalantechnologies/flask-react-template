import os
import time
import uuid
from typing import Iterator

import pytest

from modules.config.config_service import ConfigService
from modules.config.internal.config_manager import ConfigManager
from modules.core.cache_service import CacheService
from modules.core.errors import CacheDiscardFailedError, CacheNonPositiveTTLError
from modules.core.internal.cache.cache_client import CacheClient
from modules.core.internal.cache.cache_manager import DEFAULT_KEY_PREFIX

CACHE_LOGGER = "modules.logger.internal.console_logger"
UNREACHABLE_REDIS_URL = "redis://127.0.0.1:1/0"


def _unique_key() -> str:
    return f"test-{uuid.uuid4().hex}"


def _reload_config() -> None:
    ConfigService.config_manager = ConfigManager()


@pytest.fixture(autouse=True)
def isolated_cache_client() -> Iterator[None]:
    _reload_config()
    CacheClient.reset()
    yield
    CacheClient.reset()


@pytest.fixture
def unreachable_redis(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    monkeypatch.setenv("CELERY_BROKER_URL", UNREACHABLE_REDIS_URL)
    _reload_config()
    CacheClient.reset()
    yield


class TestGivenAReachableRedis:
    class TestWhenAValueIsSetThenRead:
        def test_then_the_stored_value_comes_back(self) -> None:
            key = _unique_key()

            CacheService.set(key=key, value="stored-value", ttl_seconds=30)

            assert CacheService.get(key=key) == "stored-value"

    class TestWhenAKeyWasNeverWritten:
        def test_then_the_read_reports_a_miss(self) -> None:
            assert CacheService.get(key=_unique_key()) is None

    class TestWhenTheTimeToLiveElapses:
        def test_then_the_entry_is_gone(self) -> None:
            key = _unique_key()

            CacheService.set(key=key, value="short-lived", ttl_seconds=1)
            time.sleep(1.5)

            assert CacheService.get(key=key) is None

    class TestWhenAnEntryIsDiscarded:
        def test_then_the_next_read_reports_a_miss(self) -> None:
            key = _unique_key()
            CacheService.set(key=key, value="to-be-discarded", ttl_seconds=30)

            CacheService.discard(key=key)

            assert CacheService.get(key=key) is None

    class TestWhenDiscardingAKeyThatIsNotPresent:
        def test_then_it_completes_without_raising(self) -> None:
            CacheService.discard(key=_unique_key())

    class TestWhenTheKeyIsNamespaced:
        def test_then_the_stored_key_carries_the_configured_prefix(self) -> None:
            key = _unique_key()
            prefix = ConfigService[str].get_value(key="cache.key_prefix", default=DEFAULT_KEY_PREFIX)

            CacheService.set(key=key, value="namespaced", ttl_seconds=30)

            assert CacheClient.get_client().exists(f"{prefix}:{key}") == 1

    class TestWhenTheConfiguredPrefixChanges:
        def test_then_the_new_prefix_namespaces_the_entry(self, monkeypatch: pytest.MonkeyPatch) -> None:
            key = _unique_key()
            monkeypatch.setenv("CACHE_KEY_PREFIX", "another-product")
            _reload_config()

            CacheService.set(key=key, value="namespaced", ttl_seconds=30)

            assert CacheClient.get_client().exists(f"another-product:{key}") == 1


class TestGivenAConfigWithoutACachePrefix:
    class TestWhenAValueIsWritten:
        def test_then_the_built_in_default_prefix_is_used(self, monkeypatch: pytest.MonkeyPatch) -> None:
            key = _unique_key()
            config_manager = ConfigManager()
            config_manager.config_store.pop("cache", None)
            monkeypatch.setattr(ConfigService, "config_manager", config_manager)

            CacheService.set(key=key, value="defaulted", ttl_seconds=30)

            assert CacheClient.get_client().exists(f"{DEFAULT_KEY_PREFIX}:{key}") == 1


class TestGivenANonPositiveTimeToLive:
    class TestWhenAWriteIsAttempted:
        @pytest.mark.parametrize("ttl_seconds", [0, -1])
        def test_then_the_write_is_rejected(self, ttl_seconds: int) -> None:
            key = _unique_key()

            with pytest.raises(CacheNonPositiveTTLError):
                CacheService.set(key=key, value="rejected", ttl_seconds=ttl_seconds)

            assert CacheService.get(key=key) is None


class TestGivenRedisIsUnreachable:
    class TestWhenAValueIsRead:
        def test_then_it_reports_a_miss_and_warns(
            self, unreachable_redis: None, caplog: pytest.LogCaptureFixture
        ) -> None:
            with caplog.at_level("WARNING", logger=CACHE_LOGGER):
                value = CacheService.get(key=_unique_key())

            assert value is None
            assert any("cache read failed" in record.getMessage() for record in caplog.records)

    class TestWhenAValueIsWritten:
        def test_then_it_does_nothing_and_warns(
            self, unreachable_redis: None, caplog: pytest.LogCaptureFixture
        ) -> None:
            with caplog.at_level("WARNING", logger=CACHE_LOGGER):
                CacheService.set(key=_unique_key(), value="never-stored", ttl_seconds=30)

            assert any("cache write failed" in record.getMessage() for record in caplog.records)

    class TestWhenAnEntryIsDiscarded:
        def test_then_it_raises_so_the_stale_entry_is_never_ignored(self, unreachable_redis: None) -> None:
            with pytest.raises(CacheDiscardFailedError):
                CacheService.discard(key=_unique_key())


class TestGivenTheProcessIdChanges:
    class TestWhenTheClientIsRequestedAgain:
        def test_then_the_connection_pool_is_rebuilt(self, monkeypatch: pytest.MonkeyPatch) -> None:
            client_before_fork = CacheClient.get_client()
            forked_pid = os.getpid() + 1

            monkeypatch.setattr(os, "getpid", lambda: forked_pid)
            client_after_fork = CacheClient.get_client()

            assert client_after_fork is not client_before_fork
            assert client_after_fork.connection_pool is not client_before_fork.connection_pool

    class TestWhenTheProcessIdIsUnchanged:
        def test_then_the_same_client_is_reused(self) -> None:
            assert CacheClient.get_client() is CacheClient.get_client()
