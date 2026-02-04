from typing import Any

import requests

from modules.application.worker import Worker
from modules.config.config_service import ConfigService
from modules.logger.logger import Logger


class HealthCheckWorker(Worker):
    """
    Periodic health check worker that monitors the backend API availability.

    This worker is designed for monitoring/alerting purposes. It catches all exceptions
    and logs them rather than re-raising, because health checks should not fail or retry -
    they are diagnostic and should always complete, reporting the health status observed.
    """

    queue = "default"
    max_retries = 1
    cron_schedule = "*/10 * * * *"  # Every 10 minutes

    @classmethod
    def perform(cls, *args: Any, **kwargs: Any) -> None:
        health_check_url = ConfigService[str].get_value("worker.health_check_url", default="http://localhost:8080/api/")

        try:
            res = requests.get(health_check_url, timeout=3)

            if res.status_code == 200:
                Logger.info(message="Backend is healthy")
            else:
                Logger.error(message=f"Backend is unhealthy: status {res.status_code}")

        except Exception as e:
            Logger.error(message=f"Backend is unhealthy: {e}")
