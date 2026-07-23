import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Iterator

import pytest

from modules.config.config_service import ConfigService
from modules.config.internal.config_manager import ConfigManager
from modules.core.common.types import ActorType, AuditActor
from modules.core.jobs.health_check_job import HealthCheckJob

JOB_ACTOR = AuditActor(actor_type=ActorType.JOB, actor_id="test-run")
HEALTH_CHECK_LOGGER = "modules.logger.internal.console_logger"


class _StatusHandler(BaseHTTPRequestHandler):
    status_code = 200

    def do_GET(self) -> None:  # noqa: N802
        self.send_response(self.status_code)
        self.end_headers()

    def log_message(self, *_args: object) -> None:
        return


@pytest.fixture
def health_server() -> Iterator[str]:
    server = HTTPServer(("127.0.0.1", 0), _StatusHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address[0], server.server_address[1]
    try:
        yield f"http://{host!s}:{port}/"
    finally:
        server.shutdown()
        thread.join()


def _point_health_check_at(monkeypatch: pytest.MonkeyPatch, url: str) -> None:
    monkeypatch.setenv("HEALTH_CHECK_URL", url)
    monkeypatch.setattr(ConfigService, "config_manager", ConfigManager())


class TestGivenTheBackendResponds:
    class TestWhenHealthCheckReturns200:
        def test_then_logs_healthy_status(
            self, health_server: str, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
        ) -> None:
            _StatusHandler.status_code = 200
            _point_health_check_at(monkeypatch, health_server)

            with caplog.at_level("INFO", logger=HEALTH_CHECK_LOGGER):
                HealthCheckJob.perform(actor=JOB_ACTOR)

            assert any("Backend is healthy" in record.getMessage() for record in caplog.records)

    class TestWhenHealthCheckReturns500:
        def test_then_logs_unhealthy_status(
            self, health_server: str, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
        ) -> None:
            _StatusHandler.status_code = 500
            _point_health_check_at(monkeypatch, health_server)

            with caplog.at_level("ERROR", logger=HEALTH_CHECK_LOGGER):
                HealthCheckJob.perform(actor=JOB_ACTOR)

            assert any("Backend is unhealthy: status 500" in record.getMessage() for record in caplog.records)


class TestGivenTheBackendIsUnreachable:
    class TestWhenTheConnectionIsRefused:
        def test_then_logs_unhealthy_status(
            self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
        ) -> None:
            _point_health_check_at(monkeypatch, "http://127.0.0.1:1/")

            with caplog.at_level("ERROR", logger=HEALTH_CHECK_LOGGER):
                HealthCheckJob.perform(actor=JOB_ACTOR)

            assert any("Backend is unhealthy:" in record.getMessage() for record in caplog.records)


class TestGivenJobConfiguration:
    class TestWhenInspectingJobSettings:
        def test_then_has_expected_queue_and_schedule(self) -> None:
            assert HealthCheckJob.queue == "default"
            assert HealthCheckJob.max_retries == 1
            assert HealthCheckJob.cron_schedule == "*/10 * * * *"
