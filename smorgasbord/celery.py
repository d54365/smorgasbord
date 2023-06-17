import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smorgasbord.settings")

app = Celery("smorgasbord")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
