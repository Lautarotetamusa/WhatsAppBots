from __future__ import absolute_import, unicode_literals

import os

from celery import Celery, shared_task
#from home import tasks

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "home.settings")

app = Celery("home")

#Ejecutar una task cada cierto tiempo
app.conf.beat_schedule = {
      'add-every-30-seconds': {
        'task': 'home.tasks.test_task',
        'schedule': 10.0,
        'args': ()
    },
}

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
