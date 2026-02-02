# Workers

This document describes the background job processing system using Celery workers.

## Overview

The application uses Celery for background job processing with Redis as the message broker. Workers process async jobs while the main web application handles HTTP requests.

## Architecture

- **Celery Workers**: Process background jobs from queues
- **Celery Beat**: Scheduler for recurring tasks (cron jobs)
- **Redis**: Message broker and result backend
- **Flower**: Web-based monitoring dashboard

## Queue Priority

Jobs are processed in priority order:
1. `critical` - High priority jobs
2. `default` - Standard jobs  
3. `low` - Low priority jobs

## Creating Workers

Workers inherit from the `Worker` base class:

```python
from modules.application.worker import Worker

class MyWorker(Worker):
    queue = "default"
    max_retries = 3
    cron_schedule = "*/10 * * * *"  # Every 10 minutes (optional)
    
    @classmethod
    def perform(cls, *args, **kwargs):
        # Your job logic here
        pass
```

## Running Jobs

```python
# Run immediately
MyWorker.perform_async(arg1, arg2)

# Run at specific time
MyWorker.perform_at(datetime.now() + timedelta(hours=1), arg1, arg2)

# Run after delay
MyWorker.perform_in(300, arg1, arg2)  # 5 minutes
```

## Development

### Local Development

```bash
# Start all services (includes workers)
npm run serve

# Start individual services
npm run serve:worker   # Celery worker
npm run serve:beat     # Celery beat scheduler
npm run serve:flower   # Flower dashboard
```

### Monitoring

- **Flower Dashboard**: http://localhost:5555
- **Redis CLI**: `redis-cli` to inspect queues

## Production

Workers run in separate Kubernetes pods with:
- **Preview**: 1 replica, 8 concurrency
- **Production**: 3 replicas, 8 concurrency

### Scaling

```bash
# Scale preview workers
kubectl scale deployment flask-react-template-preview-worker-deployment --replicas=5 -n flask-react-template-preview

# Scale production workers  
kubectl scale deployment flask-react-template-production-worker-deployment --replicas=10 -n flask-react-template-production
```

## Configuration

Environment variables:
- `CELERY_BROKER_URL`: Redis connection for job queue
- `CELERY_RESULT_BACKEND`: Redis connection for results

## Example Workers

### Health Check Worker

Monitors application health every 10 minutes:

```python
from modules.application.workers.health_check_worker import HealthCheckWorker

# Runs automatically via cron schedule
# Manual execution:
HealthCheckWorker.perform_async()
```
