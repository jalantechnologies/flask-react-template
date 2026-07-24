from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, ClassVar, Optional

from celery import Task
from celery.result import AsyncResult
from celery.schedules import crontab
from redbeat import RedBeatSchedulerEntry

from modules.core.celery_app import app as celery_app
from modules.core.common.types import ActorType, AuditActor, JobArguments
from modules.core.internal.job_run.job_run_service import JobRunService
from modules.logger.logger import Logger


class Job(ABC):
    queue: ClassVar[str] = "default"
    max_retries: ClassVar[int] = 3
    retry_backoff: ClassVar[bool] = True
    retry_backoff_max: ClassVar[int] = 600
    cron_schedule: ClassVar[Optional[str]] = None

    @classmethod
    @abstractmethod
    def perform(cls, *args: Any, actor: AuditActor, **kwargs: Any) -> Any:
        """Run the job body. `actor` identifies this specific run so every write the body makes is
        attributed to the job_run record; subclasses thread it into their repository calls."""

    @classmethod
    def perform_async(cls, *args: Any, **kwargs: Any) -> AsyncResult:
        task = cls._get_celery_task()
        return task.apply_async(args=args, kwargs=kwargs)

    @classmethod
    def perform_at(cls, run_at: datetime, *args: Any, **kwargs: Any) -> AsyncResult:
        task = cls._get_celery_task()
        return task.apply_async(args=args, kwargs=kwargs, eta=run_at)

    @classmethod
    def perform_in(cls, delay_seconds: int, *args: Any, **kwargs: Any) -> AsyncResult:
        task = cls._get_celery_task()
        return task.apply_async(args=args, kwargs=kwargs, countdown=delay_seconds)

    @classmethod
    def _run_with_job_run(cls, task: Task, args: tuple[Any, ...], kwargs: dict[str, Any]) -> Any:
        job_run = JobRunService.start(
            job_name=cls.__name__,
            arguments=cls._describe_arguments(args, kwargs),
            retry_count=task.request.retries or 0,
        )
        actor = AuditActor(actor_type=ActorType.JOB, actor_id=job_run.id)
        try:
            result = cls.perform(*args, actor=actor, **kwargs)
        except Exception:
            JobRunService.mark_failed(job_run_id=job_run.id)
            raise
        JobRunService.mark_succeeded(job_run_id=job_run.id)
        return result

    @staticmethod
    def _describe_arguments(args: tuple[Any, ...], kwargs: dict[str, Any]) -> JobArguments:
        described: JobArguments = {f"arg_{index}": Job._describe_value(value) for index, value in enumerate(args)}
        for name, value in kwargs.items():
            described[name] = Job._describe_value(value)
        return described

    @staticmethod
    def _describe_value(value: Any) -> Optional[str | int | float | bool]:
        return value if isinstance(value, (str, int, float, bool)) or value is None else str(value)

    @classmethod
    def _get_celery_task(cls) -> Task:
        task_name = f"{cls.__module__}.{cls.__name__}"

        if task_name in celery_app.tasks:
            return celery_app.tasks[task_name]

        @celery_app.task(
            name=task_name,
            bind=True,
            queue=cls.queue,
            max_retries=cls.max_retries,
            autoretry_for=(Exception,),
            retry_backoff=cls.retry_backoff,
            retry_backoff_max=cls.retry_backoff_max,
            retry_jitter=True,
        )
        def celery_task(self: Task, *args: Any, **kwargs: Any) -> Any:
            return cls._run_with_job_run(self, args, kwargs)

        return celery_task

    @classmethod
    def register(cls) -> None:
        cls.register_task()
        cls.register_cron()
        if cls.cron_schedule:
            Logger.info(message=f"Registered job {cls.__name__} with cron schedule: {cls.cron_schedule}")
        else:
            Logger.info(message=f"Registered job {cls.__name__}")

    @classmethod
    def register_task(cls) -> None:
        cls._get_celery_task()

    @classmethod
    def register_cron(cls) -> None:
        if not cls.cron_schedule:
            return

        parts = cls.cron_schedule.split()
        if len(parts) != 5:
            raise ValueError(
                f"Invalid cron schedule '{cls.cron_schedule}' for {cls.__name__}. "
                f"Expected format: 'minute hour day month day_of_week'"
            )

        minute, hour, day_of_month, month_of_year, day_of_week = parts
        task = cls._get_celery_task()

        entry = RedBeatSchedulerEntry(
            name=f"{cls.__module__}.{cls.__name__}_cron",
            task=task.name,
            schedule=crontab(
                minute=minute,
                hour=hour,
                day_of_month=day_of_month,
                month_of_year=month_of_year,
                day_of_week=day_of_week,
            ),
            app=celery_app,
        )
        entry.save()
