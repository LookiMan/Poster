from os import environ

from celery import Celery

environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery(environ['CELERY_APP'])
app.config_from_object('config.settings', namespace='CELERY')
app.autodiscover_tasks()
