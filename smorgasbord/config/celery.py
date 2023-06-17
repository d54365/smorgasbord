from ..env import env

CELERY_BROKER_URL = env("CELERY_BROKER_URL")
CELERY_TIMEZONE = "UTC"

CELERY_TASK_SOFT_TIME_LIMIT = 70  # seconds
CELERY_TASK_TIME_LIMIT = 60  # seconds
CELERY_TASK_MAX_RETRIES = 3
CELERYD_MAX_TASKS_PER_CHILD = 100
