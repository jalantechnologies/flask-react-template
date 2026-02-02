from modules.application.worker import Worker
from modules.logger.logger import Logger


class HealthCheckWorker(Worker):
    """
    Example worker that runs every 10 minutes to verify the worker system is functioning.
    """

    cron_schedule = "*/10 * * * *"  # Every 10 minutes
    queue = "default"

    @classmethod
    def perform(cls) -> str:
        Logger.info(message="HealthCheckWorker: System is healthy")
        return "OK"
