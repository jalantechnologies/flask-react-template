from typing import Any

import requests

from modules.config.config_service import ConfigService
from modules.core.common.types import AuditActor
from modules.core.job import Job
from modules.logger.logger import Logger


class HealthCheckJob(Job):
    queue = "default"
    max_retries = 1
    cron_schedule = "*/10 * * * *"

    @classmethod
    def perform(cls, *args: Any, actor: AuditActor, **kwargs: Any) -> None:
        health_check_url = ConfigService[str].get_value("worker.health_check_url", default="http://localhost:8080/api/")

        try:
            res = requests.get(health_check_url, timeout=3)

            if res.status_code == 200:
                Logger.info(message="Backend is healthy")
            else:
                Logger.error(message=f"Backend is unhealthy: status {res.status_code}")

        except Exception as e:
            Logger.error(message=f"Backend is unhealthy: {e}")
