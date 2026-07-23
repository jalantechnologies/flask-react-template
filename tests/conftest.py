import os
from typing import Iterator, cast

import pytest
from celery_app import app as celery_app

from modules.logger.logger_manager import LoggerManager

TESTING_APP_ENV = "testing"


@pytest.fixture(scope="session", autouse=True)
def mount_loggers() -> None:
    # Logger mounting configures process-global state and is only meaningful once per process, exactly
    # as it runs once at server boot. Doing it here, session-scoped, is the correct home for it. Running
    # it in per-test setup stacked a duplicate handler for every test and multiplied log output.
    LoggerManager.mount_logger()


def _running_against_testing_broker() -> bool:
    return os.environ.get("APP_ENV", "development") == TESTING_APP_ENV


def _broker_queue_names() -> list[str]:
    return [getattr(queue, "name", queue) for queue in (celery_app.conf.task_queues or [])]


def _purge_broker_queues() -> None:
    if not _running_against_testing_broker():
        return
    with celery_app.connection_for_write() as connection:
        for name in _broker_queue_names():
            connection.default_channel.queue_purge(name)


def broker_queue_depth(name: str) -> int:
    with celery_app.connection_for_write() as connection:
        return cast(int, connection.default_channel._size(name))


@pytest.fixture(autouse=True)
def purge_broker_queues() -> Iterator[None]:
    _purge_broker_queues()
    yield
    _purge_broker_queues()
