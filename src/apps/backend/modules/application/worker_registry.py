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
            path=modules_pkg.__path__, prefix=modules_pkg.__name__ + ".", onerror=lambda _: None
        ):
            if ispkg and modname.endswith(".internals.workers"):
                packages.append(modname)
        return packages

    @staticmethod
    def _register_worker(obj: Type[Worker]) -> None:
        if obj.cron_schedule:
            obj.register_cron()
            Logger.info(message=f"Registered worker {obj.__name__} with cron schedule: {obj.cron_schedule}")
        else:
            Logger.info(message=f"Registered worker {obj.__name__}")

    @staticmethod
    def _register_workers_from_package(pkg_name: str) -> list[Type[Worker]]:
        workers: list[Type[Worker]] = []
        try:
            pkg = importlib.import_module(pkg_name)
        except ImportError as e:
            if pkg_name in WorkerRegistry._WORKER_PACKAGES:
                raise
            Logger.error(message=f"Failed to import worker package {pkg_name}: {e}")
            return workers

        for _importer, modname, _ispkg in pkgutil.walk_packages(path=pkg.__path__, prefix=pkg.__name__ + "."):
            try:
                module = importlib.import_module(modname)
                for _name, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, Worker) and obj is not Worker and obj.__module__ == modname:
                        workers.append(obj)
                        WorkerRegistry._register_worker(obj)
            except Exception as e:
                Logger.error(message=f"Failed to import worker module {modname}: {e}")

        return workers

    @staticmethod
    def discover_and_register_workers() -> list[Type[Worker]]:
        workers: list[Type[Worker]] = []
        for pkg_name in WorkerRegistry._discover_worker_packages():
            workers.extend(WorkerRegistry._register_workers_from_package(pkg_name))
        return workers

    @staticmethod
    def initialize() -> None:
        Logger.info(message="Initializing worker registry...")
        workers = WorkerRegistry.discover_and_register_workers()
        Logger.info(message=f"Registered {len(workers)} workers")
