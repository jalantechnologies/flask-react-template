import importlib
import pkgutil
from dataclasses import dataclass
from types import ModuleType
from typing import Iterator, Optional, Type

from modules.core.job import Job
from modules.logger.logger import Logger


@dataclass(frozen=True)
class JobsPackage:
    PACKAGE_NAME = "jobs"

    name: str
    package: ModuleType

    @classmethod
    def of_module(cls, module_name: str) -> Optional["JobsPackage"]:
        name = f"{module_name}.{cls.PACKAGE_NAME}"
        try:
            return cls(name=name, package=importlib.import_module(name))
        except ModuleNotFoundError:
            return None

    def load_jobs(self) -> None:
        for _, job_module_name, _ in pkgutil.iter_modules(self.package.__path__, prefix=f"{self.name}."):
            importlib.import_module(job_module_name)


class JobRegistry:
    ROOT_PACKAGE = "modules"

    @classmethod
    def initialize(cls) -> None:
        for jobs_package in cls._jobs_packages():
            jobs_package.load_jobs()

        jobs = cls._loaded_jobs()
        for job in jobs:
            job.register()

        Logger.info(message=f"Registered {len(jobs)} jobs")

    @classmethod
    def _jobs_packages(cls) -> Iterator[JobsPackage]:
        root = importlib.import_module(cls.ROOT_PACKAGE)
        for _, module_name, is_package in pkgutil.iter_modules(root.__path__, prefix=f"{cls.ROOT_PACKAGE}."):
            if not is_package:
                continue

            jobs_package = JobsPackage.of_module(module_name)
            if jobs_package is not None:
                yield jobs_package

    @classmethod
    def _loaded_jobs(cls) -> list[Type[Job]]:
        return sorted(Job.__subclasses__(), key=lambda job: job.__name__)
