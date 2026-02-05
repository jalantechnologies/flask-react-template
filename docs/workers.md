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

## Creating Workers

All workers inherit from the base `Worker` class which provides a Sidekiq-style API:

```python
from modules.application.worker import Worker
from modules.logger.logger import Logger

class MyBackgroundWorker(Worker):
    # Worker configuration
    queue = "default"                    # Queue assignment
    max_retries = 3                     # Retry failed jobs up to 3 times
    retry_backoff = True                # Use exponential backoff
    retry_backoff_max = 600             # Max 10 minutes between retries
    cron_schedule = "0 2 * * *"         # Optional: run daily at 2 AM

    @classmethod
    def perform(cls, user_id: int, data: dict) -> None:
        """
        Main job logic. This method is called when the job executes.

        Args:
            user_id: ID of the user to process
            data: Additional data for processing
        """
        try:
            # Your job logic here
            Logger.info(message=f"Processing user {user_id}")
            # ... processing logic ...
            Logger.info(message=f"Completed processing user {user_id}")
        except Exception as e:
            Logger.error(message=f"Failed to process user {user_id}: {e}")
            raise  # Re-raise to trigger retry mechanism
```

### Worker Configuration Options

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

The Worker base class provides several methods for job execution:

### Immediate Execution

```python
# Queue job for immediate processing
result = MyBackgroundWorker.perform_async(user_id=123, data={"key": "value"})

# Get job ID for tracking
job_id = result.id
print(f"Job queued with ID: {job_id}")
```

### Scheduled Execution

```python
from datetime import datetime, timedelta

# Schedule job for specific time
run_time = datetime.now() + timedelta(hours=2)
result = MyBackgroundWorker.perform_at(run_time, user_id=123, data={"key": "value"})

# Schedule job with delay
result = MyBackgroundWorker.perform_in(
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

## Worker Registry

Workers are automatically discovered and registered on application startup via the `WorkerRegistry`:

```python
# In server.py
from modules.application.worker_registry import WorkerRegistry

# Initialize worker registry (discovers all workers)
WorkerRegistry.initialize()
```

The registry:

- Scans `modules.application.workers/` for Worker subclasses
- Registers Celery tasks for each worker
- Sets up cron schedules for workers with `cron_schedule` defined
- Logs registration details for debugging

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

1. Create worker in `src/apps/backend/modules/application/workers/`
2. Worker is automatically discovered on next server restart
3. Test via Flower dashboard or direct API calls
4. Monitor execution in Flower at http://localhost:5555

### Bootstrap Behavior

The backend application runs bootstrap tasks once at startup:

- Database seeding (test users, initial data)
- Worker registry initialization (discovers and registers all worker classes)

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

Workers use the application's logging system:

```python
from modules.logger.logger import Logger

class MyWorker(Worker):
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
│  CPU < 70%     CPU < 70%       CPU > 70%        CPU > 70%      │
│                                 (scale up)      (max reached)   │
└─────────────────────────────────────────────────────────────────┘
```

**HPA Configuration:**

| Parameter         | Value | Description                              |
| ----------------- | ----- | ---------------------------------------- |
| `minReplicas`     | 1     | Cost saving during idle periods          |
| `maxReplicas`     | 5     | Maximum pods for high load               |
| `targetCPU`       | 70%   | Scale up when CPU exceeds this threshold |
| `scaleUpWindow`   | 30s   | React quickly to load increases          |
| `scaleDownWindow` | 300s  | Wait 5 min before scaling down           |

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
| Medium load (20-30 concurrent) | 2-3      | CPU exceeds 70%           |
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
| **Low traffic API** | Keep defaults (min:1, max:5, 70%)             |
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

Queues are automatically configured in `celery_app.py`:

```python
task_queues = {
    "critical": {"exchange": "critical", "routing_key": "critical"},
    "default": {"exchange": "default", "routing_key": "default"},
    "low": {"exchange": "low", "routing_key": "low"},
}
```

## Example Workers

### Health Check Worker

Monitors application health every 10 minutes:

```python
# File: modules/application/workers/health_check_worker.py
from typing import Any
import requests
from modules.application.worker import Worker
from modules.config.config_service import ConfigService
from modules.logger.logger import Logger

class HealthCheckWorker(Worker):
    queue = "default"
    max_retries = 1
    cron_schedule = "*/10 * * * *"  # Every 10 minutes

    @classmethod
    def perform(cls, *args: Any, **kwargs: Any) -> None:
        # URL is configurable via HEALTH_CHECK_URL env var or config
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
HealthCheckWorker.perform_async()

# Automatic execution via cron (every 10 minutes)
# No code needed - runs automatically when beat scheduler is active
```

### Data Processing Worker

Example worker for processing user data:

```python
# File: modules/application/workers/data_processing_worker.py
from typing import Any, Dict
from modules.application.worker import Worker
from modules.logger.logger import Logger

class DataProcessingWorker(Worker):
    queue = "default"
    max_retries = 3

    @classmethod
    def perform(cls, user_id: int, processing_options: Dict[str, Any]) -> Dict[str, Any]:
        Logger.info(message=f"Starting data processing for user {user_id}")

        try:
            # Simulate data processing
            processed_data = {
                "user_id": user_id,
                "status": "completed",
                "processed_at": "2024-01-01T00:00:00Z",
                "options": processing_options
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
result = DataProcessingWorker.perform_async(
    user_id=123,
    processing_options={"format": "json", "include_metadata": True}
)

# Schedule for later
from datetime import datetime, timedelta
DataProcessingWorker.perform_at(
    datetime.now() + timedelta(hours=1),
    user_id=123,
    processing_options={"format": "csv"}
)
```

## Best Practices

### Error Handling

Always handle exceptions properly in workers:

```python
class MyWorker(Worker):
    @classmethod
    def perform(cls, data):
        try:
            # Job logic here
            pass
        except SpecificException as e:
            Logger.error(message=f"Specific error: {e}")
            # Don't re-raise if you want to mark job as completed
        except Exception as e:
            Logger.error(message=f"Unexpected error: {e}")
            raise  # Re-raise to trigger retry mechanism
```

### Idempotency

Make workers idempotent (safe to run multiple times):

```python
class IdempotentWorker(Worker):
    @classmethod
    def perform(cls, record_id: int):
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
class ResourceAwareWorker(Worker):
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

### Testing Workers

Test workers in isolation:

```python
# In tests/modules/application/test_my_worker.py
from modules.application.workers.my_worker import MyWorker

class TestMyWorker:
    def test_perform_success(self):
        # Test successful execution
        result = MyWorker.perform(test_data="valid")
        assert result["status"] == "success"

    def test_perform_failure(self):
        # Test error handling
        with pytest.raises(ValueError):
            MyWorker.perform(test_data="invalid")
```

## Testing Workers

### In Tests

Workers execute synchronously in tests (no Redis needed):

```python
from modules.application.workers.my_worker import MyWorker

def test_worker_execution():
    # Execute immediately in tests
    MyWorker.perform(data="test_data")

    # Verify results
    assert expected_result
```

### Manual Testing

```python
# In a Python shell
from modules.application.workers.health_check_worker import HealthCheckWorker

# Run immediately
HealthCheckWorker.perform()

# Queue for async execution
result = HealthCheckWorker.perform_async()

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

class CustomWorker(Worker):
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
    FirstWorker._get_celery_task().s(data="123"),
    SecondWorker._get_celery_task().s(),
    ThirdWorker._get_celery_task().s(),
)
workflow.apply_async()
```

### Task Groups

```python
from celery import group

# Execute tasks in parallel
job = group(
    ProcessWorker._get_celery_task().s(item_id="1"),
    ProcessWorker._get_celery_task().s(item_id="2"),
    ProcessWorker._get_celery_task().s(item_id="3"),
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

- Increase `task_time_limit` in celery_app.py
- Break large jobs into smaller tasks
- Use `perform_in()` for delayed processing

**Cron Jobs Not Running:**

1. Verify beat scheduler is running:
   ```bash
   celery -A celery_app inspect scheduled
   ```
2. Check worker logs for cron registration:
   ```
   Registered worker HealthCheckWorker with cron schedule: */10 * * * *
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
celery -A celery_app inspect active

# View registered tasks
celery -A celery_app inspect registered
```
