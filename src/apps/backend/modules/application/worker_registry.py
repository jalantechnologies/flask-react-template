import importlib
import inspect
import pkgutil
from typing import Type

from modules.application.worker import Worker
from modules.logger.logger import Logger


class WorkerRegistry:
    @staticmethod
    def discover_and_register_workers() -> list[Type[Worker]]:
        workers: list[Type[Worker]] = []

        # Import the workers package to trigger task registration
        import modules.application.workers as workers_package

        # Walk through all modules in the workers package
        for importer, modname, ispkg in pkgutil.walk_packages(
            path=workers_package.__path__, prefix=workers_package.__name__ + "."
        ):
            try:
                module = importlib.import_module(modname)

                # Find all Worker subclasses in this module
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if (
                        issubclass(obj, Worker)
                        and obj is not Worker
                        and obj.__module__ == modname
                    ):
                        workers.append(obj)

                        # Register cron schedule if defined
                        if obj.cron_schedule:
                            obj.register_cron()
                            Logger.info(
                                message=f"Registered worker {obj.__name__} with cron schedule: {obj.cron_schedule}"
                            )
                        else:
                            Logger.info(message=f"Registered worker {obj.__name__}")

            except Exception as e:
                Logger.error(message=f"Failed to import worker module {modname}: {e}")

        return workers

    @staticmethod
    def initialize() -> None:
        Logger.info(message="Initializing worker registry...")
        workers = WorkerRegistry.discover_and_register_workers()
        Logger.info(message=f"Registered {len(workers)} workers")
