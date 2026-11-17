# Gunicorn configuration file for production
import multiprocessing

# Server socket
bind = "0.0.0.0:5000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 5

# Server mechanics
daemon = False
pidfile = "/tmp/gunicorn.pid"
umask = 0
user = None
group = None
tmp_upload_dir = "/tmp"

# Logging
errorlog = "-"
accesslog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "erp01"


# Server hooks
def on_starting(server):
    print("ERP01 starting...")


def on_reload(server):
    print("ERP01 reloading...")


def worker_int(worker):
    print(f"Worker {worker.pid} received INT signal")
