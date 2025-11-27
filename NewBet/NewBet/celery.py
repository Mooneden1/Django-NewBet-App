import os
from celery import Celery
from django.conf import settings

# settings for celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NewBet.settings')
app = Celery('NewBet')

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

#section for periodic tasks
app.conf.beat_schedule = {
    'check-fixtures-every-3-minutes': {
        'task': 'betapp.tasks.check_fixtures',
        'schedule': crontab(minute='*/3'),  # Every 3 minutes
    },
}