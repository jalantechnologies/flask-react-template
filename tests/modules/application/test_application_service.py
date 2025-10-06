import pytest
from temporalio.client import WorkflowExecutionStatus

from modules.application.application_service import ApplicationService
from modules.application.errors import WorkerIdNotFoundError, WorkerNotRegisteredError
from modules.application.types import BaseWorker
from modules.application.workers.health_check_worker import HealthCheckWorker
from modules.logger.logger import Logger
from tests.modules.application.base_test_application import BaseTestApplication


class TestApplicationService(BaseTestApplication):
    def test_run_worker_immediately(self) -> None:
        """Given a registered worker, when run immediately, then it completes successfully."""

        self.require_temporal_server()

        # Given a registered worker class
        worker_cls = HealthCheckWorker

        # When the worker is triggered immediately
        worker_id = ApplicationService.run_worker_immediately(cls=worker_cls)

        # Then the worker eventually completes the run
        assert worker_id
        worker_details = self.wait_for_worker_status(
            worker_id=worker_id, expected_status=WorkflowExecutionStatus.COMPLETED
        )
        assert worker_details.id == worker_id

    def test_schedule_worker_as_cron(self) -> None:
        """Given a cron schedule, when scheduling a worker, then it runs until terminated."""

        self.require_temporal_server()

        # Given a cron schedule for the health check worker
        cron_schedule = "*/1 * * * *"

        # When the worker is scheduled
        worker_id = ApplicationService.schedule_worker_as_cron(cls=HealthCheckWorker, cron_schedule=cron_schedule)

        # Then the worker starts running and can be terminated deterministically
        assert worker_id
        running_worker = self.wait_for_worker_status(
            worker_id=worker_id, expected_status=WorkflowExecutionStatus.RUNNING
        )
        assert running_worker.id == worker_id

        ApplicationService.terminate_worker(worker_id=worker_id)

        terminated_worker = self.wait_for_worker_status(
            worker_id=worker_id, expected_status=WorkflowExecutionStatus.TERMINATED
        )
        assert terminated_worker.id == worker_id

    def test_run_worker_with_unregistered_worker(self) -> None:
        """Given an unknown worker, when executed, then a registration error is raised."""

        class UnRegisteredWorker(BaseWorker):
            def run(self) -> None: ...

        with pytest.raises(WorkerNotRegisteredError):
            ApplicationService.run_worker_immediately(cls=UnRegisteredWorker)

    def test_get_details_with_invalid_worker_id(self) -> None:
        """Given an invalid worker id, when queried, then a not found error is raised."""

        self.require_temporal_server()

        with pytest.raises(WorkerIdNotFoundError):
            ApplicationService.get_worker_by_id(worker_id="invalid_id")

    def test_duplicate_cron_not_scheduled(self) -> None:
        """Given an existing cron worker, when scheduling the same cron, then the original worker is reused."""

        self.require_temporal_server()

        log_messages: list[str] = []

        def fake_info(message: str) -> None:
            log_messages.append(message)

        with pytest.MonkeyPatch.context() as monkeypatch:
            monkeypatch.setattr(Logger, "info", fake_info)

            cron_schedule = "*/1 * * * *"

            # Given an already running cron worker
            worker_id_first = ApplicationService.schedule_worker_as_cron(
                cls=HealthCheckWorker, cron_schedule=cron_schedule
            )
            assert worker_id_first
            self.wait_for_worker_status(worker_id=worker_id_first, expected_status=WorkflowExecutionStatus.RUNNING)

            # When scheduling the same worker again
            worker_id_duplicate = ApplicationService.schedule_worker_as_cron(
                cls=HealthCheckWorker, cron_schedule=cron_schedule
            )

        # Then the duplicate request is ignored and logged
        assert worker_id_first == worker_id_duplicate
        duplicate_log = f"Worker {worker_id_first} already running, skipping starting new instance"
        assert any(duplicate_log in log for log in log_messages), "Expected duplicate log message not found"

        ApplicationService.terminate_worker(worker_id=worker_id_first)
        self.wait_for_worker_status(worker_id=worker_id_first, expected_status=WorkflowExecutionStatus.TERMINATED)
