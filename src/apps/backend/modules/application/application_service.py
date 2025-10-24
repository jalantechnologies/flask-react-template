from typing import Any, Tuple, Type

from modules.application.internal.worker_manager import WorkerManager
from modules.application.types import BaseWorker, Worker


class ApplicationService:
    @staticmethod
    def connect_temporal_server() -> None:
        return WorkerManager.connect_temporal_server()

    @staticmethod
    def get_worker_by_id(*, worker_id: str) -> Worker:
        return WorkerManager.get_worker_by_id(worker_id=worker_id)

    @staticmethod
    def run_worker_immediately(*, cls: Type[BaseWorker], arguments: Tuple[Any, ...] = ()) -> str:
        return WorkerManager.run_worker_immediately(cls=cls, arguments=arguments)

    @staticmethod
    def schedule_worker_as_cron(*, cls: Type[BaseWorker], cron_schedule: str) -> str:
        return WorkerManager.schedule_worker_as_cron(cls=cls, cron_schedule=cron_schedule)

    @staticmethod
    def cancel_worker(*, worker_id: str) -> None:
        return WorkerManager.cancel_worker(worker_id=worker_id)

    @staticmethod
    def terminate_worker(*, worker_id: str) -> None:
        return WorkerManager.terminate_worker(worker_id=worker_id)
