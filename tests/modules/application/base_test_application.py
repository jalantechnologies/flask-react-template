import time
import unittest
from typing import Callable

import pytest
from temporalio.client import WorkflowExecutionStatus

from modules.application.application_service import ApplicationService
from modules.application.errors import WorkerClientConnectionError
from modules.logger.logger_manager import LoggerManager


class BaseTestApplication(unittest.TestCase):
    """Shared helpers for Temporal worker related tests."""

    POLL_INTERVAL_SECONDS = 0.1
    DEFAULT_TIMEOUT_SECONDS = 10

    def setup_method(self, method: Callable) -> None:
        print(f"Executing:: {method.__name__}")
        LoggerManager.mount_logger()
        # The Temporal server is not started by the tests. Individual test cases can
        # opt-in to require it via ``require_temporal_server``.

    def teardown_method(self, method: Callable) -> None:
        print(f"Executed:: {method.__name__}")

    def wait_for_worker_status(
        self, *, worker_id: str, expected_status: WorkflowExecutionStatus, timeout_seconds: float | None = None
    ):
        """Polls Temporal until the worker reaches the expected status."""

        deadline = time.monotonic() + (timeout_seconds or self.DEFAULT_TIMEOUT_SECONDS)
        last_status: WorkflowExecutionStatus | None = None

        while time.monotonic() < deadline:
            worker = ApplicationService.get_worker_by_id(worker_id=worker_id)
            last_status = worker.status
            if last_status == expected_status:
                return worker
            time.sleep(self.POLL_INTERVAL_SECONDS)

        raise AssertionError(f"Worker {worker_id} expected status {expected_status} but observed {last_status}")

    def require_temporal_server(self) -> None:
        """Skip the test if a Temporal server is not reachable."""

        try:
            ApplicationService.connect_temporal_server()
        except WorkerClientConnectionError as error:
            pytest.skip(f"Temporal server unavailable: {error}")
