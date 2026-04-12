import os

from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop_api.settings')

app = Celery('shop_api')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

from celery.beat import crontab
app.conf.beat_schedule = {
    "send_birthday_message": {
        "task": "users.tasks.send_birthday_message",
        "schedule": crontab(minute="*")
    }
}

app.conf.beat_schedule = {
    "delete-inactive-users-every-day": {
        "task": "users.tasks.delete_inactive_users",
        "schedule": crontab(hour=0, minute=0),  
    }
}