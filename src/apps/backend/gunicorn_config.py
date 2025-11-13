import multiprocessing

# Server Socket
bind = "0.0.0.0:8080"

# Worker Processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gthread"
threads = 2 * multiprocessing.cpu_count()

# Logging
loglevel = "info"
accesslog = "-"
access_log_format = "app - request - %(h)s - %(s)s - %(m)s - %(M)sms - %(U)s - %({user-agent}i)s"
errorlog = "-"

# Timeout
timeout = 30
keepalive = 2
