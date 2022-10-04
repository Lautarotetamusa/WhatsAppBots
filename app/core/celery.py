from __future__ import absolute_import, unicode_literals

import os

from celery import Celery, shared_task
from celery.schedules import crontab

from utils.timefunctions import parse_time
from datetime import time

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

app = Celery("celery")

app.conf.beat_schedule = {
#Task que se ejecuta todos los dias a las 00:00hs en LOCAL_TIME_ZONE
  'manage_campaigns': {
    'task': 'home.tasks.manage_campaign',
    'schedule': crontab(0, parse_time(time(0,0)).hour),
    'args': ()
    },
}

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
