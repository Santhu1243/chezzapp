from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'alert-overdue-issues-every-15-mins': {
        'task': 'nonsap.tasks.check_and_alert_overdue_issues',
        'schedule': crontab(minute='*/15'),  # every 15 minutes
    },
}
