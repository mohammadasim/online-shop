from __future__ import absolute_import
import os
from celery import Celery

# set the default Django setting module for the celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'online_shop.settings.dev')

# We create an instance of the application
app = Celery('online_shop')

# We load any custom config from project settings, using the
# config_from_object() method. The namespace attribute specifies the
# prefix that celery-related settings will have in settings.py file.
# By setting 'CELERY' namespace, all celery settings need to include
# 'CELERY_' prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Finally we tell celery to auto-discover asynchronous tasks for
# the application. Celery will look for tasks.py file in each
# application directory of applications added to INSTALLED_APPS
# in order to load asynchronous task defined in them.
app.autodiscover_tasks()


# We need to import the celery module in the __init__.py file of
# our projects to make sure it is loaded when Django starts.
# We edit __init__.py in online_shops and updated it.

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
