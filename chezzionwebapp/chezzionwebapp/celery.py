# chezzionwebapp/celery.py

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

# Set default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chezzionwebapp.settings')

app = Celery('chezzionwebapp')

# Load settings from Django's config using the CELERY_ namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Autodiscover tasks from all installed apps
app.autodiscover_tasks()

# Define beat schedule
app.conf.beat_schedule = {
    'check-overdue-issues-every-5-minutes': {
        'task': 'nonsap.tasks.check_and_alert_overdue_issues',
        'schedule': crontab(minute='*/5'),
    },
}
