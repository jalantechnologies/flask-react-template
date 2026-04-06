import importlib
import inspect
import pkgutil
from typing import Type

from modules.application.worker import Worker
from modules.logger.logger import Logger


class WorkerRegistry:
    _WORKER_PACKAGES = ["modules.application.workers"]

    @staticmethod
    def _discover_worker_packages() -> list[str]:
        modules_pkg = importlib.import_module("modules")
        packages = list(WorkerRegistry._WORKER_PACKAGES)
        for _importer, modname, ispkg in pkgutil.walk_packages(
            path=modules_pkg.__path__,
            prefix=modules_pkg.__name__ + ".",
            onerror=lambda _: None,
        ):
            if ispkg and modname.endswith(".internals.workers"):
                packages.append(modname)
        return packages

    @staticmethod
    def discover_and_register_workers() -> list[Type[Worker]]:
        workers: list[Type[Worker]] = []

        for pkg_name in WorkerRegistry._discover_worker_packages():
            try:
                pkg = importlib.import_module(pkg_name)
            except ImportError:
                continue

            for _importer, modname, _ispkg in pkgutil.walk_packages(
                path=pkg.__path__, prefix=pkg.__name__ + "."
            ):
                try:
                    module = importlib.import_module(modname)

                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if issubclass(obj, Worker) and obj is not Worker and obj.__module__ == modname:
                            workers.append(obj)

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
