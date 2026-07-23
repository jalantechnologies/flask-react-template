from typing import Iterator
from unittest.mock import patch

import pytest
from celery_app import app as celery_app
from redbeat.schedulers import RedBeatConfig, get_redis

from modules.application.worker_registry import WorkerRegistry
from modules.application.workers.health_check_worker import HealthCheckWorker

HEALTH_CHECK_TASK_NAME = "modules.application.workers.health_check_worker.HealthCheckWorker"
HEALTH_CHECK_CRON_ENTRY = f"{HEALTH_CHECK_TASK_NAME}_cron"


@pytest.fixture
def eager_execution() -> Iterator[None]:
    previous_always_eager = celery_app.conf.task_always_eager
    previous_eager_propagates = celery_app.conf.task_eager_propagates
    celery_app.conf.task_always_eager = True
    celery_app.conf.task_eager_propagates = True
    try:
        yield
    finally:
        celery_app.conf.task_always_eager = previous_always_eager
        celery_app.conf.task_eager_propagates = previous_eager_propagates


class TestGivenTheCeleryAppIsImported:
    class TestWhenInspectingTheTaskRegistry:
        def test_then_the_worker_task_is_registered_without_a_lazy_dispatch(self) -> None:
            assert HEALTH_CHECK_TASK_NAME in celery_app.tasks


class TestGivenWorkersAreRegistered:
    class TestWhenTheRegistryInitializes:
        def test_then_the_cron_entry_is_persisted_to_the_redbeat_schedule(self) -> None:
            redis = get_redis(celery_app)
            config = RedBeatConfig(celery_app)
            schedule_key = config.schedule_key
            entry_key = f"{config.key_prefix}{HEALTH_CHECK_CRON_ENTRY}"
            redis.delete(schedule_key, entry_key)

            WorkerRegistry.initialize()

            members = set(redis.zrange(schedule_key, 0, -1))
            assert entry_key in members
            assert redis.exists(entry_key)


class TestGivenAWorkerTaskIsDispatched:
    class TestWhenTheHealthCheckReturns200:
        def test_then_the_worker_body_executes(self, eager_execution: None) -> None:
            with (
                patch("modules.application.workers.health_check_worker.requests.get") as mock_get,
                patch("modules.application.workers.health_check_worker.Logger.info") as mock_info,
            ):
                mock_get.return_value.status_code = 200

                result = HealthCheckWorker.perform_async()

                assert result.successful()
                mock_get.assert_called_once()
                mock_info.assert_called_once_with(message="Backend is healthy")
