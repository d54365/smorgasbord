from __future__ import print_function

import multiprocessing
import os

workers_per_core_str = os.getenv("WORKERS_PER_CORE", "2")
web_concurrency_str = os.getenv("WEB_CONCURRENCY", None)
host = os.getenv("HOST", "0.0.0.0")
port = os.getenv("PORT", "80")
bind_env = os.getenv("BIND", None)
use_loglevel = os.getenv("LOG_LEVEL", "info")
if bind_env:
    use_bind = bind_env
else:
    use_bind = "{host}:{port}".format(host=host, port=port)

cores = multiprocessing.cpu_count()
workers_per_core = float(workers_per_core_str)
default_web_concurrency = workers_per_core * cores + 1
if web_concurrency_str:
    web_concurrency = int(web_concurrency_str)
    assert web_concurrency > 0
else:
    web_concurrency = int(default_web_concurrency)

# Gunicorn config variables
backlog = 2048
reload = False
daemon = False
loglevel = use_loglevel
workers = web_concurrency
worker_class = "gthread"
threads = cores * 2
bind = use_bind
keepalive = 60
graceful_timeout = 60
timeout = 30

accesslog = "-"
errorlog = "logs/gunicorn_error.log"
