from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional, Type

from temporalio import workflow
from temporalio.client import WorkflowExecutionStatus
from temporalio.common import RetryPolicy


class WorkerPriority(Enum):
    DEFAULT = "DEFAULT"
    CRITICAL = "CRITICAL"


class BaseWorker(ABC):
    """
    Base class for all Temporal workers.
    """

    priority: WorkerPriority = WorkerPriority.DEFAULT
    max_execution_time_in_seconds: int = 600
    max_retries: int = 3

    @staticmethod
    @abstractmethod
    async def execute(*args: Any) -> None:
        """
        Subclasses must implement the execute() method, where the worker logic goes
        """

    @abstractmethod
    async def run(self, *args: Any) -> None:
        """
        Subclasses must implement the run() method, which is the application's entry point
        """
        await workflow.execute_activity(
            self.execute,
            args=args,
            start_to_close_timeout=timedelta(seconds=self.max_execution_time_in_seconds),
            retry_policy=RetryPolicy(maximum_attempts=self.max_retries),
        )


@dataclass(frozen=True)
class RegisteredWorker:
    cls: Type[BaseWorker]
    priority: WorkerPriority


@dataclass(frozen=True)
class Worker:
    id: str
    status: Optional[WorkflowExecutionStatus]
    start_time: datetime
    close_time: Optional[datetime]
    task_queue: str
    worker_type: str
