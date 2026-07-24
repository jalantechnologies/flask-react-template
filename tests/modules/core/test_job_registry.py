from redbeat import RedBeatSchedulerEntry
from redbeat.schedulers import RedBeatConfig

from modules.core.celery_app import app as celery_app
from modules.core.jobs.health_check_job import HealthCheckJob

HEALTH_CHECK_TASK_NAME = "modules.core.jobs.health_check_job.HealthCheckJob"


class TestGivenTheWorkerEntrypointIsImported:
    class TestWhenInspectingRegisteredTasks:
        def test_then_the_health_check_job_is_in_app_tasks(self) -> None:
            import worker_app

            assert HEALTH_CHECK_TASK_NAME in worker_app.app.tasks


class TestGivenAJobHasACronSchedule:
    class TestWhenTheJobRegistersItsCron:
        def test_then_the_entry_persists_to_the_redbeat_redis_schedule(self) -> None:
            HealthCheckJob.register_cron()

            schedule_name = f"{HealthCheckJob.__module__}.{HealthCheckJob.__name__}_cron"
            entry = RedBeatSchedulerEntry.from_key(
                f"{RedBeatConfig(celery_app).key_prefix}{schedule_name}", app=celery_app
            )

            assert entry.task == HEALTH_CHECK_TASK_NAME
