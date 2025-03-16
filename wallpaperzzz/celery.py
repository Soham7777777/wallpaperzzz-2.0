from celery import Celery
from celery.app.task import Task
import django_stubs_ext
import os


Task.__class_getitem__ = classmethod(lambda cls, *args, **kwargs: cls) # type: ignore[attr-defined]

django_stubs_ext.monkeypatch()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wallpaperzzz.settings')
os.environ.setdefault('FLOWER_UNAUTHENTICATED_API', 'true')
app = Celery('wallpaperzzz')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
