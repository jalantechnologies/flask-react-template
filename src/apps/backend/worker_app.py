from dotenv import load_dotenv

load_dotenv()

from celery.signals import beat_init, worker_ready

from modules.core.celery_app import app
from modules.core.job_registry import JobRegistry

# Register at import, before the worker snapshots app.tasks into its consumption strategies; a task
# registered only after that snapshot is rejected as unregistered even while present in app.tasks.
JobRegistry.initialize()


@worker_ready.connect
def reregister_jobs_on_worker_ready(sender: object = None, **kwargs: object) -> None:
    JobRegistry.initialize()


@beat_init.connect
def reregister_jobs_on_beat_init(sender: object = None, **kwargs: object) -> None:
    JobRegistry.initialize()


__all__ = ["app"]
