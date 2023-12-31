# config/celery.py

import os
from celery import Celery
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

#let it use the right configuration setting from our settings file
configuration = os.getenv('ENVIRONMENT', 'development').title()
os.environ.setdefault('DJANGO_CONFIGURATION', configuration)

import configurations
configurations.setup()

app = Celery('config')

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))