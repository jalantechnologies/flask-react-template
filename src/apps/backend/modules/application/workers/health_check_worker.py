from typing import Any

import requests

from modules.application.types import BaseWorker
from modules.logger.logger import Logger


class HealthCheckWorker(BaseWorker):
    max_execution_time_in_seconds = 10
    max_retries = 1

    @staticmethod
    async def execute(*args: Any) -> None:
        try:
            res = requests.get("http://localhost:8080/api/", timeout=3)

            if res.status_code == 200:
                Logger.info(message="Backend is healthy")

            else:
                Logger.error(message="Backend is unhealthy")

        except Exception as e:
            Logger.error(message=f"Backend is unhealthy: {e}")

    async def run(self, *args: Any) -> None:
        await super().run(*args)
