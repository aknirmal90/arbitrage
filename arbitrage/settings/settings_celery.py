import os
from celery.schedules import crontab

######################################################################
# Celery Settings
######################################################################

CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]

CELERY_TIMEZONE = 'Asia/Kolkata'

CELERY_IGNORE_RESULT = True

CELERYD_MAX_TASKS_PER_CHILD = 200  # Restart a worker process after executing 200 tasks

CELERY_ACKS_LATE = True  # Messages need to be acknowledged twice

# Time limits in seconds.
CELERYD_TASK_TIME_LIMIT = os.getenv('CELERYD_TASK_TIME_LIMIT', 9000)

CELERYBEAT_SCHEDULE = {
    'register-withdrawals': {
        'task': 'markets.tasks.SyncTicker',
        'schedule': crontab(minute='*'),
    },
}

CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://127.0.0.1:6379/0')
