from __future__ import absolute_import
from celery import Celery
import os

from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE",
                      'messenger.settings')

app = Celery('messenger')

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(settings.INSTALLED_APPS)
