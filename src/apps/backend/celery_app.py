from celery import Celery
from celery.schedules import crontab
from redbeat import RedBeatSchedulerEntry

from modules.config.config_service import ConfigService

app = Celery("foundation")

# Load configuration
app.conf.update(
    broker_url=ConfigService[str].get_value("celery.broker_url"),
    result_backend=ConfigService[str].get_value("celery.result_backend"),
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,
    task_soft_time_limit=25 * 60,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    broker_connection_retry_on_startup=True,
    # Use RedBeat scheduler to store schedule in Redis (compatible with read-only filesystem)
    beat_scheduler="redbeat.RedBeatScheduler",
    redbeat_redis_url=ConfigService[str].get_value("celery.broker_url"),
    # Define task queues with priority levels
    # Workers will process higher priority queues first
    task_queues={
        "critical": {
            "exchange": "critical",
            "routing_key": "critical",
        },
        "default": {
            "exchange": "default",
            "routing_key": "default",
        },
        "low": {
            "exchange": "low",
            "routing_key": "low",
        },
    },
    task_default_queue="default",
    task_default_exchange="default",
    task_default_routing_key="default",
)

# Beat schedule for cron jobs
# Workers can also register themselves here
app.conf.beat_schedule = {}

# Auto-discover tasks from all modules
app.autodiscover_tasks(
    [
        "modules.application.workers",
    ]
)

# Initialize worker registry to register cron schedules
from modules.application.worker_registry import WorkerRegistry
WorkerRegistry.initialize()
