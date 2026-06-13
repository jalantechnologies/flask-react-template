import pytest

from modules.logger.logger_manager import LoggerManager


@pytest.fixture(scope="session", autouse=True)
def mount_loggers() -> None:
    # Logger mounting configures process-global state and is only meaningful once per process, exactly
    # as it runs once at server boot. Doing it here, session-scoped, is the correct home for it. Running
    # it in per-test setup stacked a duplicate handler for every test and multiplied log output.
    LoggerManager.mount_logger()
