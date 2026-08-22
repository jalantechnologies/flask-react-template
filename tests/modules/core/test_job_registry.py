from abc import abstractmethod
from typing import Any

from redbeat import RedBeatSchedulerEntry
from redbeat.schedulers import RedBeatConfig

from modules.core.celery_app import app as celery_app
from modules.core.common.types import AuditActor
from modules.core.job import Job
from modules.core.job_registry import JobRegistry
from modules.core.jobs.health_check_job import HealthCheckJob

HEALTH_CHECK_TASK_NAME = "modules.core.jobs.health_check_job.HealthCheckJob"


class BaseSyncJob(Job):
    @classmethod
    @abstractmethod
    def perform(cls, *args: Any, actor: AuditActor, **kwargs: Any) -> Any:
        pass


class SyncUsersJob(BaseSyncJob):
    @classmethod
    def perform(cls, *args: Any, actor: AuditActor, **kwargs: Any) -> None:
        return None


class TestGivenTheWorkerEntrypointIsImported:
    class TestWhenInspectingRegisteredTasks:
        def test_then_the_health_check_job_is_in_app_tasks(self) -> None:
            import worker_app

            assert HEALTH_CHECK_TASK_NAME in worker_app.app.tasks


class TestGivenAJobInheritsFromAnIntermediateAbstractBase:
    class TestWhenCollectingLoadedJobs:
        def test_then_the_indirect_subclass_is_collected(self) -> None:
            assert SyncUsersJob in JobRegistry._loaded_jobs()

        def test_then_the_abstract_base_is_not_collected(self) -> None:
            assert BaseSyncJob not in JobRegistry._loaded_jobs()

        def test_then_the_direct_subclass_is_still_collected(self) -> None:
            assert HealthCheckJob in JobRegistry._loaded_jobs()

        def test_then_each_job_is_collected_once(self) -> None:
            jobs = JobRegistry._loaded_jobs()

            assert len(jobs) == len(set(jobs))


class TestGivenAJobHasACronSchedule:
    class TestWhenTheJobRegistersItsCron:
        def test_then_the_entry_persists_to_the_redbeat_redis_schedule(self) -> None:
            HealthCheckJob.register_cron()

            schedule_name = f"{HealthCheckJob.__module__}.{HealthCheckJob.__name__}_cron"
            entry = RedBeatSchedulerEntry.from_key(
                f"{RedBeatConfig(celery_app).key_prefix}{schedule_name}", app=celery_app
            )

            assert entry.task == HEALTH_CHECK_TASK_NAME
