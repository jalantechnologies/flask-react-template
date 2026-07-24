# Workers

Flask-React-Template uses **Celery** with **Redis** for background job processing and scheduled tasks.

---

## Overview

Workers run independently from the web server, allowing:

- Async job processing (e.g., document parsing, data imports)
- Scheduled/recurring tasks (e.g., health checks, data syncing)
- Independent scaling (2 web pods, 20 worker pods)

```
┌──────────┐      ┌───────┐      ┌────────────┐
│ Web App  │─────►│ Redis │─────►│   Worker   │
│ (Flask)  │      │(Broker)│      │  (Celery)  │
└──────────┘      └───────┘      └────────────┘
   Queue job        Store job      Execute job
```

## Architecture

The worker system consists of several components:

- **Celery Workers**: Process background jobs from Redis queues
- **Celery Beat**: Scheduler for recurring tasks (cron jobs)
- **Redis**: Message broker for job queues and result storage
- **Flower**: Web-based monitoring dashboard for workers and tasks

### Queue System

Jobs are processed in priority order across three queues:

1. **`critical`** - High priority jobs that need immediate processing
2. **`default`** - Standard background jobs
3. **`low`** - Low priority jobs processed when workers are idle

Workers consume from all queues but prioritize higher priority queues first.

## Creating Jobs

A **job** is the unit of async work; a **worker** is the Celery process that runs it. All jobs inherit from the base `Job` class, which provides a Sidekiq-style API. A job lives in the public `jobs/` package of the domain that owns it (`modules/<module>/jobs/`):

```python
from typing import Any

from modules.core.common.types import AuditActor
from modules.core.job import Job
from modules.logger.logger import Logger


class MyBackgroundJob(Job):
    queue = "default"
    max_retries = 3
    retry_backoff = True
    retry_backoff_max = 600
    cron_schedule = "0 2 * * *"

    @classmethod
    def perform(cls, *args: Any, actor: AuditActor, **kwargs: Any) -> None:
        user_id = kwargs["user_id"]
        Logger.info(message=f"Processing user {user_id}")
        # Thread `actor` into every repository call so each write attributes to this run.
```

`perform` receives an `actor: AuditActor` keyword identifying the specific run. Thread it into every repository call the job makes, so those writes attribute to the job's `job_run` record.

### Job Configuration Options

| Option              | Type   | Default     | Description                             |
| ------------------- | ------ | ----------- | --------------------------------------- |
| `queue`             | `str`  | `"default"` | Queue name for job routing              |
| `max_retries`       | `int`  | `3`         | Maximum retry attempts for failed jobs  |
| `retry_backoff`     | `bool` | `True`      | Use exponential backoff between retries |
| `retry_backoff_max` | `int`  | `600`       | Maximum seconds between retries         |
| `cron_schedule`     | `str`  | `None`      | Cron expression for recurring jobs      |

### Cron Schedule Format

Cron schedules use standard 5-field format: `minute hour day month day_of_week`

```python
# Examples
cron_schedule = "0 2 * * *"      # Daily at 2:00 AM
cron_schedule = "*/15 * * * *"   # Every 15 minutes
cron_schedule = "0 9 * * 1"      # Every Monday at 9:00 AM
cron_schedule = "0 0 1 * *"      # First day of every month at midnight
```

## Running Jobs

The Job base class provides several methods for job execution:

### Immediate Execution

```python
# Queue job for immediate processing
result = MyBackgroundJob.perform_async(user_id=123, data={"key": "value"})

# Get job ID for tracking
job_id = result.id
print(f"Job queued with ID: {job_id}")
```

### Scheduled Execution

```python
from datetime import datetime, timedelta

# Schedule job for specific time
run_time = datetime.now() + timedelta(hours=2)
result = MyBackgroundJob.perform_at(run_time, user_id=123, data={"key": "value"})

# Schedule job with delay
result = MyBackgroundJob.perform_in(
    delay_seconds=300,  # 5 minutes
    user_id=123,
    data={"key": "value"}
)
```

### Job Result Tracking

```python
from celery.result import AsyncResult

# Check job status
result = AsyncResult(job_id)
print(f"Status: {result.status}")
print(f"Result: {result.result}")

# Wait for completion (blocking)
try:
    final_result = result.get(timeout=60)  # Wait up to 60 seconds
    print(f"Job completed: {final_result}")
except Exception as e:
    print(f"Job failed: {e}")
```

## Job Registry

Jobs are automatically discovered and registered at entrypoint import via the `JobRegistry`:

```python
# In web_app.py and worker_app.py
from modules.core.job_registry import JobRegistry

# Discover jobs and register their Celery tasks
JobRegistry.initialize()
```

The registry:

- Imports every `modules/*/jobs/` package (public surface, never `internal/`)
- Registers a Celery task for each immediate `Job` subclass
- Persists cron schedules to the RedBeat Redis store for jobs with `cron_schedule` defined
- Runs at entrypoint import, before the worker snapshots its task table, so a queued message is never rejected as an unregistered task

## Job Run Records

Every execution writes a `job_run` row (job name, redacted arguments, start/end time, status `running` → `succeeded` | `failed`, retry count). The `Job` base creates it at the start of the run and finalizes it on completion or failure. The run's id becomes the job's audit actor (`AuditActor(ActorType.JOB, job_run_id)`), so every write the job makes joins back to a concrete run. This gives both a trustworthy audit actor and job observability (history, status, retries) for free.

## Development

### Local Development Setup

1. **Start Redis** (required for job queues):

   ```bash
   redis-server
   ```

2. **Start all services** (recommended):

   ```bash
   npm run serve  # Starts backend, frontend, workers, beat, and flower
   ```

3. **Start individual services**:
   ```bash
   npm run serve:backend  # Flask API only
   npm run serve:worker   # Celery worker only
   npm run serve:beat     # Celery beat scheduler only
   npm run serve:flower   # Flower dashboard only
   ```

### Development Workflow

1. Create a job in `src/apps/backend/modules/<module>/jobs/`
2. The job is automatically discovered at the next entrypoint restart
3. Test via Flower dashboard or direct API calls
4. Monitor execution in Flower at http://localhost:5555

### Bootstrap Behavior

The backend application runs bootstrap tasks once at startup:

- Database seeding (test users, initial data)
- Job registry initialization (discovers and registers all job classes)

**Gunicorn Configuration:**

The application uses `preload_app = True` in `gunicorn_config.py`. This ensures:

- Bootstrap tasks run **once** in the master process before forking workers
- All workers inherit the fully initialized application state
- No duplicate bootstrap execution across workers

Without `preload_app`, each of the worker processes would run bootstrap tasks independently, causing duplicate database writes and initialization overhead.

### Monitoring and Debugging

#### Flower Dashboard

Access at http://localhost:5555 for:

- Active workers and their status
- Job queue lengths and processing rates
- Individual job details and results
- Worker resource usage (CPU, memory)
- Failed job inspection and retry

#### Redis CLI Inspection

```bash
# Connect to Redis
redis-cli

# List all keys
KEYS *

# Check queue lengths
LLEN default       # Default queue
LLEN critical      # Critical queue
LLEN low           # Low priority queue

# Inspect job data
LRANGE default 0 -1  # View all jobs in default queue
```

#### Logging

Jobs use the application's logging system:

```python
from modules.logger.logger import Logger

class MyJob(Job):
    @classmethod
    def perform(cls, data):
        Logger.info(message="Starting job processing")
        # ... job logic ...
        Logger.info(message="Job completed successfully")
```

## Production Deployment

### Kubernetes Architecture

Workers run in separate Kubernetes deployments from the web application:

```
┌─────────────────────────────────────────────────┐
│                 Namespace                        │
│                                                 │
│  ┌─────────────┐  ┌─────────────────────────────┐ │
│  │   Web Pod   │  │       Worker Pod            │ │
│  │             │  │                             │ │
│  │ - Flask API │  │ - Celery Worker (8 workers) │ │
│  │ - React App │  │ - Celery Beat (scheduler)   │ │
│  │             │  │ - Flower (monitoring)       │ │
│  └─────────────┘  └─────────────────────────────┘ │
│         │                        │                │
│         └────────┬─────────────────┘                │
│                  │                                │
│            ┌─────────────┐                        │
│            │ Redis Pod   │                        │
│            │ (Message    │                        │
│            │  Broker)    │                        │
│            └─────────────┘                        │
└─────────────────────────────────────────────────┘
```

### Environment Configuration

| Environment    | Worker Replicas | Concurrency | Resources           | Autoscaling |
| -------------- | --------------- | ----------- | ------------------- | ----------- |
| **Preview**    | 1               | 8           | 200m CPU, 512Mi RAM | No          |
| **Production** | 1 (default)     | 8           | 500m CPU, 1Gi RAM   | HPA (1-5)   |

### Autoscaling (HPA)

Production workers use **Horizontal Pod Autoscaler (HPA)** to automatically scale based on CPU utilization:

```
┌─────────────────────────────────────────────────────────────────┐
│                    HPA Scaling Behavior                         │
│                                                                 │
│  Idle          Light Load      Medium Load      Heavy Load      │
│  1 pod    →    1 pod      →    2-3 pods    →    4-5 pods       │
│                                                                 │
│  CPU < 80%     CPU < 80%       CPU > 80%        CPU > 80%      │
│                                 (scale up)      (max reached)   │
└─────────────────────────────────────────────────────────────────┘
```

**HPA Configuration:**

| Parameter         | Value | Description                                     |
| ----------------- | ----- | ----------------------------------------------- |
| `minReplicas`     | 1     | Cost saving during idle periods                 |
| `maxReplicas`     | 5     | Maximum pods for high load                      |
| `targetCPU`       | 80%   | Scale up when CPU exceeds this threshold        |
| `scaleUpWindow`   | 30s   | React quickly to load increases                 |
| `scaleDownWindow` | 180s  | Wait 3 min before scaling down (shared cluster) |

**How it works with DigitalOcean Cluster Autoscaler:**

1. **Load increases** → HPA adds worker pods
2. **Pods can't be scheduled** → DO Cluster Autoscaler adds nodes
3. **Load decreases** → HPA removes worker pods (after 5 min)
4. **Nodes underutilized** → DO Cluster Autoscaler removes nodes

**Monitoring HPA:**

```bash
# Watch HPA status in real-time
kubectl get hpa -n flask-react-template-production -w

# Check HPA events and scaling decisions
kubectl describe hpa flask-react-template-production-worker-hpa \
  -n flask-react-template-production

# View current metrics
kubectl top pods -n flask-react-template-production
```

**Expected scaling behavior:**

| Scenario                       | Replicas | Trigger                   |
| ------------------------------ | -------- | ------------------------- |
| Idle (template default)        | 1        | Health check every 10 min |
| Light load (5-10 tasks/min)    | 1        | Single replica handles it |
| Medium load (20-30 concurrent) | 2-3      | CPU exceeds 80%           |
| Heavy load (50+ concurrent)    | 4-5      | Scales to max             |
| Load drops                     | Gradual  | Waits 5 min, -1 pod/min   |

### Manual Scaling

For testing or temporary overrides, workers can be scaled manually:

```bash
# Preview environment (no HPA)
kubectl scale deployment flask-react-template-preview-worker-deployment \
  --replicas=5 -n flask-react-template-preview

# Production environment (overrides HPA temporarily)
kubectl scale deployment flask-react-template-production-worker-deployment \
  --replicas=10 -n flask-react-template-production
```

> **Note:** Manual scaling in production is temporary. HPA will eventually adjust replicas back to match the target CPU utilization.

### Tuning HPA for Production Applications

When using this template for production applications, consider adjusting HPA settings:

| App Type            | Recommended Changes                           |
| ------------------- | --------------------------------------------- |
| **Low traffic API** | Keep defaults (min:1, max:5, 80%)             |
| **E-commerce**      | Increase max to 10, lower target to 60%       |
| **Data processing** | Consider KEDA with queue-based scaling        |
| **High traffic**    | Increase max, separate Beat to own deployment |

Edit `lib/kube/production/worker-hpa.yaml` to adjust settings:

```yaml
spec:
  minReplicas: 2 # Higher minimum for availability
  maxReplicas: 10 # Higher maximum for traffic spikes
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          averageUtilization: 60 # Lower threshold for faster scaling
```

### Resource Monitoring

Monitor worker resource usage:

```bash
# Check pod resource usage
kubectl top pods -n flask-react-template-production

# View worker logs
kubectl logs -f deployment/flask-react-template-production-worker-deployment \
  -c celery-worker -n flask-react-template-production

# Check Redis memory usage
kubectl exec -it deployment/flask-react-template-production-redis-deployment \
  -n flask-react-template-production -- redis-cli info memory
```

## Configuration

### Environment Variables

| Variable                | Description                      | Example                    |
| ----------------------- | -------------------------------- | -------------------------- |
| `CELERY_BROKER_URL`     | Redis connection for job queues  | `redis://localhost:6379/0` |
| `CELERY_RESULT_BACKEND` | Redis connection for job results | `redis://localhost:6379/0` |

### Queue Configuration

Queues are automatically configured in `modules/core/celery_app.py`:

```python
task_queues = {
    "critical": {"exchange": "critical", "routing_key": "critical"},
    "default": {"exchange": "default", "routing_key": "default"},
    "low": {"exchange": "low", "routing_key": "low"},
}
```

## Example Jobs

### Health Check Job

Monitors application health every 10 minutes:

```python
# File: modules/core/jobs/health_check_job.py
from typing import Any
import requests
from modules.core.common.types import AuditActor
from modules.core.job import Job
from modules.config.config_service import ConfigService
from modules.logger.logger import Logger

class HealthCheckJob(Job):
    queue = "default"
    max_retries = 1
    cron_schedule = "*/10 * * * *"

    @classmethod
    def perform(cls, *args: Any, actor: AuditActor, **kwargs: Any) -> None:
        health_check_url = ConfigService[str].get_value(
            "worker.health_check_url",
            default="http://localhost:8080/api/",
        )

        try:
            res = requests.get(health_check_url, timeout=3)
            if res.status_code == 200:
                Logger.info(message="Backend is healthy")
            else:
                Logger.error(message=f"Backend is unhealthy: status {res.status_code}")
        except Exception as e:
            Logger.error(message=f"Backend is unhealthy: {e}")
```

Usage:

```python
# Manual execution
HealthCheckJob.perform_async()

# Automatic execution via cron (every 10 minutes) once the beat scheduler is active
```

### Data Processing Job

Example job for processing user data:

```python
# File: modules/<module>/jobs/data_processing_job.py
from typing import Any, Dict
from modules.core.common.types import AuditActor
from modules.core.job import Job
from modules.logger.logger import Logger

class DataProcessingJob(Job):
    queue = "default"
    max_retries = 3

    @classmethod
    def perform(cls, *args: Any, actor: AuditActor, **kwargs: Any) -> Dict[str, Any]:
        user_id = kwargs["user_id"]
        Logger.info(message=f"Starting data processing for user {user_id}")

        try:
            processed_data = {
                "user_id": user_id,
                "status": "completed",
                "options": kwargs.get("processing_options", {}),
            }
            Logger.info(message=f"Data processing completed for user {user_id}")
            return processed_data
        except Exception as e:
            Logger.error(message=f"Data processing failed for user {user_id}: {e}")
            raise
```

Usage:

```python
# Queue processing job
result = DataProcessingJob.perform_async(
    user_id=123,
    processing_options={"format": "json", "include_metadata": True}
)

# Schedule for later
from datetime import datetime, timedelta
DataProcessingJob.perform_at(
    datetime.now() + timedelta(hours=1),
    user_id=123,
    processing_options={"format": "csv"}
)
```

## Best Practices

### Error Handling

Always handle exceptions properly in jobs. Re-raise to trigger the retry mechanism; swallow only for a diagnostic job that should always complete:

```python
class MyJob(Job):
    @classmethod
    def perform(cls, *args, actor, **kwargs):
        try:
            pass
        except SpecificException as e:
            Logger.error(message=f"Specific error: {e}")
        except Exception as e:
            Logger.error(message=f"Unexpected error: {e}")
            raise
```

### Idempotency

Make jobs idempotent (safe to run multiple times):

```python
class IdempotentJob(Job):
    @classmethod
    def perform(cls, *args, actor, **kwargs):
        record_id = kwargs["record_id"]
        # Check if already processed
        if is_already_processed(record_id):
            Logger.info(message=f"Record {record_id} already processed, skipping")
            return

        # Process record
        process_record(record_id)

        # Mark as processed
        mark_as_processed(record_id)
```

### Resource Management

Be mindful of resource usage in workers:

```python
class ResourceAwareJob(Job):
    @classmethod
    def perform(cls, large_dataset):
        # Process in chunks to avoid memory issues
        chunk_size = 1000
        for i in range(0, len(large_dataset), chunk_size):
            chunk = large_dataset[i:i + chunk_size]
            process_chunk(chunk)

            # Optional: yield control between chunks
            import time
            time.sleep(0.1)
```

### Testing Jobs

Test jobs in isolation:

Call `perform` directly with a `JOB` actor (in tests a fixed id stands in for the job_run id):

```python
# In tests/modules/<module>/test_my_job.py
from modules.core.common.types import ActorType, AuditActor
from modules.<module>.jobs.my_job import MyJob

job_actor = AuditActor(actor_type=ActorType.JOB, actor_id="test-run")

class TestMyJob:
    def test_perform_success(self):
        # Test successful execution
        result = MyJob.perform(test_data="valid", actor=job_actor)
        assert result["status"] == "success"

    def test_perform_failure(self):
        # Test error handling
        with pytest.raises(ValueError):
            MyJob.perform(test_data="invalid", actor=job_actor)
```

## Testing Jobs

### In Tests

Jobs execute synchronously in tests (no Redis needed):

```python
from modules.<module>.jobs.my_job import MyJob

def test_job_execution():
    # Execute immediately in tests
    MyJob.perform(data="test_data", actor=job_actor)

    # Verify results
    assert expected_result
```

### Manual Testing

```python
# In a Python shell
from modules.core.jobs.health_check_job import HealthCheckJob

# Run immediately
HealthCheckJob.perform(actor=job_actor)

# Queue for async execution
result = HealthCheckJob.perform_async()

# Check result
print(result.id)           # Task ID
print(result.status)       # 'PENDING', 'SUCCESS', 'FAILURE'
print(result.result)       # Return value
```

---

## Redis Configuration

### Connection Settings

Redis configuration is set in config files:

```yaml
# config/development.yml
celery:
  broker_url: 'redis://localhost:6379/0'
  result_backend: 'redis://localhost:6379/0'

# config/testing.yml
celery:
  broker_url: 'redis://localhost:6379/1'  # Different database
  result_backend: 'redis://localhost:6379/1'
```

### Production Considerations

For production, consider:

- **Redis persistence**: Enable AOF (append-only file) for durability
- **Memory limits**: Set `maxmemory` and `maxmemory-policy`
- **Monitoring**: Track Redis memory usage, connection count
- **Backups**: Regular Redis snapshots

Already configured in `lib/kube/production/worker-deployment.yaml`.

---

## Advanced Usage

### Custom Task Options

```python
from celery import Task

class CustomJob(Job):
    @classmethod
    def perform(cls):
        task = cls._get_celery_task()

        # Access Celery task instance
        print(task.request.id)        # Task ID
        print(task.request.retries)   # Current retry count
```

### Task Chains

```python
from celery import chain

# Execute tasks in sequence
workflow = chain(
    FirstJob._get_celery_task().s(data="123"),
    SecondJob._get_celery_task().s(),
    ThirdJob._get_celery_task().s(),
)
workflow.apply_async()
```

### Task Groups

```python
from celery import group

# Execute tasks in parallel
job = group(
    ProcessJob._get_celery_task().s(item_id="1"),
    ProcessJob._get_celery_task().s(item_id="2"),
    ProcessJob._get_celery_task().s(item_id="3"),
)
result = job.apply_async()
```

---

## Troubleshooting

### Common Issues

**Workers not starting:**

- Check Redis connection
- Verify `CELERY_BROKER_URL` environment variable
- Check worker logs for import errors

**Jobs not executing:**

- Verify worker is consuming from correct queue
- Check Flower dashboard for worker status
- Inspect Redis queues for pending jobs

**High memory usage:**

- Reduce worker concurrency
- Process data in smaller chunks
- Check for memory leaks in job logic

**Jobs timing out:**

- Increase `task_time_limit` in `modules/core/celery_app.py`
- Break large jobs into smaller tasks
- Use `perform_in()` for delayed processing

**Cron Jobs Not Running:**

1. Verify beat scheduler is running:
   ```bash
   celery -A worker_app inspect scheduled
   ```
2. Check worker logs for cron registration:
   ```
   Registered job HealthCheckJob with cron schedule: */10 * * * *
   ```
3. Ensure beat is running alongside worker:
   ```bash
   npm run serve:beat
   ```

### Debugging Commands

```bash
# Check worker status
kubectl get pods -l app=flask-react-template-worker

# View worker logs
kubectl logs -f deployment/flask-react-template-worker-deployment -c celery-worker

# View beat scheduler logs
kubectl logs -f deployment/flask-react-template-worker-deployment -c celery-beat

# Connect to Redis
kubectl exec -it deployment/flask-react-template-redis-deployment -- redis-cli

# Scale workers
kubectl scale deployment flask-react-template-worker-deployment --replicas=5

# View active workers (CLI)
celery -A worker_app inspect active

# View registered tasks
celery -A worker_app inspect registered
```
