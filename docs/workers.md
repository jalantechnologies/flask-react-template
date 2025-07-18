# Workers

This application queues background jobs that run independently of the web server using **[Temporal](https://temporal.io/)**.

---

## Defining a Worker

Create the class (typically in a `/worker` folder) and inherit from `BaseWorker`:

```python
# src/apps/backend/your_module/worker/example_worker.py
from typing import Any
from modules.application.types import BaseWorker

class ExampleWorker(BaseWorker):
    max_execution_time_in_seconds = 300   # optional
    max_retries = 5                       # optional

    async def execute(self, *args: Any) -> None:
        # Your worker logic here
        ...

    async def run(self, *args: Any) -> None:
        await super().run(*args)
```

### Optional Settings

| Attribute                       | Purpose                                                    |
|---------------------------------|------------------------------------------------------------|
| `max_execution_time_in_seconds` | Cancel execution if the worker exceeds this duration.      |
| `max_retries`                   | Maximum retry attempts before the worker is marked failed. |

---

## Registering the Worker

Add the class import to `temporal_config.py` and append it to the `WORKERS` list:

```python
from modules.application.workers.health_check_worker import HealthCheckWorker

WORKERS = [
    HealthCheckWorker,
    # other workers…
]
```

The system registers all workers with the Temporal server on startup.

---

## Controlling Workers with `ApplicationService`

| Method                                               | Description                                                                     |
|------------------------------------------------------|---------------------------------------------------------------------------------|
| `get_worker_by_id(id)`                               | Fetch a worker instance.                                                        |
| `run_worker_immediately(cls, *args)`                 | Execute a one-off worker now.                                                   |
| `schedule_worker_as_cron(cls, cron_schedule, *args)` | Run on a cron expression (`*/10 * * * *` = every 10 min).                       |
| `cancel_worker(id)`                                  | Request cancellation (requires your `run()` to catch `asyncio.CancelledError`). |
| `terminate_worker(id)`                               | Force-stop immediately.                                                         |

> **Note**: See Temporal’s [Python SDK docs on cancellation](https://docs.temporal.io/develop/python/cancellation) to understand cancellation vs. termination semantics.
