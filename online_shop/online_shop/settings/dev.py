from .base import *

DEBUG = True

ALLOWED_HOSTS = []

DATABASES = {
    'default': {
        'ENGINE': 'django_prometheus.db.backends.postgresql',
        'NAME': get_env_variable('PGSQL_DB_NAME'),
        'USER': get_env_variable('PGSQL_DB_USER'),
        'PASSWORD': get_env_variable('PGSQL_DB_PASW'),
        'HOST': get_env_variable('PGSQL_DB_HOST'),
        'PORT': get_env_variable('PGSQL_DB_PORT'),
    }
}
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
