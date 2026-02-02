# Workers

This document describes the background job processing system using Celery workers.

## Overview

The application uses Celery for background job processing with Redis as the message broker and result backend. Workers process async jobs independently from the main web application, enabling scalable background processing for tasks like data imports, document processing, and periodic maintenance.

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

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `queue` | `str` | `"default"` | Queue name for job routing |
| `max_retries` | `int` | `3` | Maximum retry attempts for failed jobs |
| `retry_backoff` | `bool` | `True` | Use exponential backoff between retries |
| `retry_backoff_max` | `int` | `600` | Maximum seconds between retries |
| `cron_schedule` | `str` | `None` | Cron expression for recurring jobs |

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
LLEN celery        # Default queue
LLEN critical      # Critical queue
LLEN low          # Low priority queue

# Inspect job data
LRANGE celery 0 -1  # View all jobs in default queue
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

| Environment | Worker Replicas | Concurrency | Resources |
|-------------|----------------|-------------|-----------|
| **Preview** | 1 | 8 | 200m CPU, 512Mi RAM |
| **Production** | 3 | 8 | 500m CPU, 1Gi RAM |

### Scaling Workers

Workers can be scaled independently from web pods:

```bash
# Preview environment
kubectl scale deployment flask-react-template-preview-worker-deployment \
  --replicas=5 -n flask-react-template-preview

# Production environment  
kubectl scale deployment flask-react-template-production-worker-deployment \
  --replicas=10 -n flask-react-template-production
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

| Variable | Description | Example |
|----------|-------------|---------|
| `CELERY_BROKER_URL` | Redis connection for job queues | `redis://localhost:6379/0` |
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
from modules.logger.logger import Logger

class HealthCheckWorker(Worker):
    queue = "default"
    max_retries = 1
    cron_schedule = "*/10 * * * *"  # Every 10 minutes
    
    @classmethod
    def perform(cls, *args: Any, **kwargs: Any) -> None:
        try:
            res = requests.get("http://localhost:8080/api/", timeout=3)
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

### Debugging Commands

```bash
# Check worker status
kubectl get pods -l app=flask-react-template-worker

# View worker logs
kubectl logs -f deployment/flask-react-template-worker-deployment -c celery-worker

# Connect to Redis
kubectl exec -it deployment/flask-react-template-redis-deployment -- redis-cli

# Scale workers
kubectl scale deployment flask-react-template-worker-deployment --replicas=5
```
