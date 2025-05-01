# thiskb/celery.py
import os
from celery import Celery

# Set the default Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "thiskb.settings")

# Create the Celery app instance
app = Celery("thiskb")

# Load configuration from Django settings
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks in all Django apps
app.autodiscover_tasks()
