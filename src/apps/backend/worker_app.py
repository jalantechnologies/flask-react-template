from dotenv import load_dotenv

load_dotenv()

from celery.signals import beat_init, worker_ready

from modules.core.celery_app import app
from modules.core.job_registry import JobRegistry

# Register every job's Celery task at import time, while `celery -A worker_app` loads this module and
# before the worker snapshots app.tasks into its consumption strategies. Registering only in the
# worker_ready signal is too late: a queued message for a task registered afterwards is rejected as
# an unregistered task even though it is in app.tasks.
JobRegistry.initialize()


@worker_ready.connect
def on_worker_ready(sender: object = None, **kwargs: object) -> None:
    JobRegistry.initialize()


@beat_init.connect
def on_beat_init(sender: object = None, **kwargs: object) -> None:
    JobRegistry.initialize()


__all__ = ["app"]
