from celery import Celery

from modules.config.config_service import ConfigService

app = Celery("foundation")

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
    beat_scheduler="redbeat.RedBeatScheduler",
    redbeat_redis_url=ConfigService[str].get_value("celery.broker_url"),
    # One beat process per deployment, so the distributed lock only serves to strand beat when a
    # previous process dies without releasing it. Disabling it keeps beat from blocking on restart.
    redbeat_lock_key=None,
    task_queues={
        "critical": {"exchange": "critical", "routing_key": "critical"},
        "default": {"exchange": "default", "routing_key": "default"},
        "low": {"exchange": "low", "routing_key": "low"},
    },
    task_default_queue="default",
    task_default_exchange="default",
    task_default_routing_key="default",
)
