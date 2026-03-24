import multiprocessing
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gunicorn.arbiter import Arbiter
    from gunicorn.workers.base import Worker

# Server Socket
bind = "0.0.0.0:8080"

# Worker Processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gthread"
threads = 2 * multiprocessing.cpu_count()

# Preload app before forking workers
# This ensures bootstrap tasks run once in the master process
preload_app = True

# Logging
loglevel = "info"
accesslog = "-"
access_log_format = "app - request - %(h)s - %(s)s - %(m)s - %(M)sms - %(U)s - %({user-agent}i)s"
errorlog = "-"


def post_fork(_server: "Arbiter", _worker: "Worker") -> None:
    """Hook to configure Gunicorn access logger to use Datadog handler after worker fork"""
    import logging

    from modules.logger.internal.datadog_handler import DatadogHandler
    from modules.logger.internal.datadog_handler_level import LogLevel

    # Get Gunicorn's access logger
    gunicorn_logger = logging.getLogger("gunicorn.access")

    # Add Datadog handler to Gunicorn's access logger
    datadog_handler = DatadogHandler("flask")
    datadog_handler.setLevel(LogLevel.get_level())
    formatter = logging.Formatter("[%(asctime)s] - %(name)s - %(levelname)s - %(message)s")
    datadog_handler.setFormatter(formatter)
    gunicorn_logger.addHandler(datadog_handler)


# Timeout
timeout = 30
keepalive = 2
