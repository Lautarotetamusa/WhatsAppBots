from __future__ import absolute_import, unicode_literals

import os

from celery import Celery, shared_task
from celery.schedules import crontab
#from home import tasks

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "home.settings")

app = Celery("home")

#Ejecutar una task cada cierto tiempo
app.conf.beat_schedule = {
      'manage_campaigns': {
        'task': 'home.tasks.test_task',
        'schedule': crontab(minute="*/1"),
        'args': ()
    },
}

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
