from celery import Celery
from celery.signals import beat_init, worker_ready

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
        "critical": {"exchange": "critical", "routing_key": "critical"},
        "default": {"exchange": "default", "routing_key": "default"},
        "low": {"exchange": "low", "routing_key": "low"},
    },
    task_default_queue="default",
    task_default_exchange="default",
    task_default_routing_key="default",
)

# Beat schedule for cron jobs
# Workers can also register themselves here
app.conf.beat_schedule = {}

# Auto-discover tasks from all modules
app.autodiscover_tasks(["modules.application.workers"])


def initialize_workers() -> None:
    """
    Initialize worker registry to register all Worker subclasses and their cron schedules.
    This must run in worker/beat processes, not just the Flask web server.
    """
    import importlib

    worker_registry_module = importlib.import_module("modules.application.worker_registry")
    worker_registry_module.WorkerRegistry.initialize()


# Register workers when Celery worker starts
@worker_ready.connect
def on_worker_ready(sender: object = None, **kwargs: object) -> None:
    initialize_workers()


# Register workers when Celery beat starts
@beat_init.connect
def on_beat_init(sender: object = None, **kwargs: object) -> None:
    initialize_workers()
