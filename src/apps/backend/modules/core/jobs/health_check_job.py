from typing import Any

from modules.config.config_service import ConfigService
from modules.core.common.types import AuditActor
from modules.core.errors import AppError
from modules.core.http.http_service import HttpService
from modules.core.job import Job
from modules.logger.logger import Logger

HEALTH_CHECK_TIMEOUT_SECONDS = 3.0


class HealthCheckJob(Job):
    queue = "default"
    max_retries = 1
    cron_schedule = "*/10 * * * *"

    @classmethod
    def perform(cls, *args: Any, actor: AuditActor, **kwargs: Any) -> None:
        health_check_url = ConfigService[str].get_value("worker.health_check_url", default="http://localhost:8080/api/")

        try:
            response = HttpService.get(
                url=health_check_url, timeout_seconds=HEALTH_CHECK_TIMEOUT_SECONDS, allow_internal_target=True
            )
        except AppError as err:
            Logger.error(message=f"Backend is unhealthy: {err.message}")
            return

        if response.is_success:
            Logger.info(message="Backend is healthy")
        else:
            Logger.error(message=f"Backend is unhealthy: status {response.status_code}")
