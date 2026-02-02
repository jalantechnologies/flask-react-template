from typing import Any

import requests

from modules.application.worker import Worker
from modules.logger.logger import Logger


class HealthCheckWorker(Worker):
    """
    Example worker that runs every 10 minutes to verify the worker system is functioning.
    """

    cron_schedule = "*/10 * * * *"  # Every 10 minutes
    queue = "default"
    max_retries = 1

    @classmethod
    def perform(cls, *args: Any, **kwargs: Any) -> None:
        try:
            res = requests.get("http://localhost:8080/api/", timeout=3)

            if res.status_code == 200:
                Logger.info(message="Backend is healthy")
            else:
                Logger.error(message=f"Backend is unhealthy: status {res.status_code}")

        except Exception as e:
            Logger.error(message=f"Backend is unhealthy: {e}")
