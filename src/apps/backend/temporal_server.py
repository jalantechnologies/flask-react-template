import asyncio

from dotenv import load_dotenv
from temporalio.client import Client
from temporalio.service import RetryConfig
from temporalio.worker import UnsandboxedWorkflowRunner, Worker

from modules.application.types import WorkerPriority
from modules.config.config_service import ConfigService
from modules.logger.logger import Logger
from modules.logger.logger_manager import LoggerManager
from temporal_config import TemporalConfig


async def main() -> None:
    load_dotenv()

    # Mount logger and workers
    LoggerManager.mount_logger()
    TemporalConfig.mount_workers()

    server_address = ConfigService[str].get_value(key="temporal.server_address")

    try:
        client = await Client.connect(server_address, retry_config=RetryConfig(max_retries=3))
    except RuntimeError:
        Logger.error(message=f"Failed to connect to Temporal server at {server_address}. Exiting...")
        return

    worker_coros = []

    # Iterate over each priority level defined in WorkerPriority enum
    for priority in WorkerPriority:
        # Filter workers for the current priority
        workers_for_priority = [
            worker.cls for worker in TemporalConfig.get_all_registered_workers() if worker.priority == priority
        ]

        # Activities for the workers of current priority
        activity_for_priority = [worker_cls.execute for worker_cls in workers_for_priority]

        # Only create a application if there are workers for that priority
        if workers_for_priority:
            task_queue = priority.value
            Logger.info(
                message=f"Starting temporal worker on queue '{task_queue}' for priority '{priority.name}' "
                f"with {len(workers_for_priority)} worker(s)."
            )
            temporal_worker = Worker(
                client,
                task_queue=task_queue,
                workflows=workers_for_priority,
                activities=activity_for_priority,
                workflow_runner=UnsandboxedWorkflowRunner(),
            )
            worker_coros.append(temporal_worker.run())

    if worker_coros:
        await asyncio.gather(*worker_coros)
    else:
        Logger.error(message="No workers registered for any priority.")


if __name__ == "__main__":
    asyncio.run(main())
