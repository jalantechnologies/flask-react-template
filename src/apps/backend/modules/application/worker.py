from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, ClassVar, Optional

from celery import Task
from celery.result import AsyncResult

from celery_app import app


class Worker(ABC):
    """
    Sidekiq-style API ensures familiar patterns for async job processing
    and cron scheduling without Rails dependency.
    """

    # Configuration (similar to sidekiq_options)
    queue: ClassVar[str] = "default"
    max_retries: ClassVar[int] = 3
    retry_backoff: ClassVar[bool] = True
    retry_backoff_max: ClassVar[int] = 600  # 10 minutes
    cron_schedule: ClassVar[Optional[str]] = None  # Cron expression (e.g., '*/10 * * * *')

    @classmethod
    @abstractmethod
    def perform(cls, *args: Any, **kwargs: Any) -> Any:
        pass

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
    def _get_celery_task(cls) -> Task:
        task_name = f"{cls.__module__}.{cls.__name__}"

        # Check if task is already registered
        if task_name in app.tasks:
            return app.tasks[task_name]

        # Create and register the task
        @app.task(
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
            return cls.perform(*args, **kwargs)

        return celery_task

    @classmethod
    def register_cron(cls) -> None:
        if not cls.cron_schedule:
            return

        from celery.schedules import crontab

        # Parse cron expression (format: minute hour day month day_of_week)
        parts = cls.cron_schedule.split()
        if len(parts) != 5:
            raise ValueError(
                f"Invalid cron schedule '{cls.cron_schedule}' for {cls.__name__}. "
                f"Expected format: 'minute hour day month day_of_week'"
            )

        minute, hour, day_of_month, month_of_year, day_of_week = parts

        schedule_name = f"{cls.__module__}.{cls.__name__}_cron"
        task = cls._get_celery_task()

        app.conf.beat_schedule[schedule_name] = {
            "task": task.name,
            "schedule": crontab(
                minute=minute,
                hour=hour,
                day_of_month=day_of_month,
                month_of_year=month_of_year,
                day_of_week=day_of_week,
            ),
        }
