import raven
from django.conf import settings
import os

print('+-----------------------------+')
print('| Azure Swarm-stg environment |')
print('+-----------------------------+\n')

# components/cache.py
CACHES = settings.CACHES
CACHES['default']['LOCATION'] = 'redis://redis:6379/0'
CACHES['api']['LOCATION'] = 'redis://redis:6379/2'

# components/task_queue.py
RQ_QUEUES = settings.RQ_QUEUES
RQ_QUEUES['default']['HOST'] = 'redis'
RQ_QUEUES['default']['PORT'] = 6379

# components/sessions.py
SESSION_REDIS = settings.SESSION_REDIS
SESSION_REDIS['host'] = 'redis'
SESSION_REDIS['port'] = 6379

try:
    raven_relase = raven.fetch_git_sha('/root/app')
except:
    raven_relase = ""

RAVEN_CONFIG = {
    'dsn': 'https://eb9325dd32f04294b9d6a82bc115ef6b:a8efa613260146f8975270583c061cd6@sentry.io/1222639',
    'release': raven_relase
}

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'activate_stg_v1',
        'USER': 'postgres@gs1activate',
        'PASSWORD': os.environ.get('DB_PASS', ''),
        'HOST': 'gs1activate.postgres.database.azure.com',
        'PORT': '5432',
    }
}

LOCALE_PATHS = (
    # "/root/app/locale",
    "/var/lib/activate/config/locale",
)

STATIC_ROOT = '/home/www-data/staticfiles'
BARCODES_FILES_PATH = '/var/lib/activate/data/barcodes/bcgen'
MEDIA_ROOT = '/var/lib/activate/data/media'
PRODUCT_IMAGE_DIR = '/var/lib/activate/data/media/product_images'

BIN_CONVERT = '/usr/bin/convert'
BIN_COMPOSITE = '/usr/bin/composite'

DEBUG = True

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# OIDC - staging
OIDC_RP_PROVIDER_ENDPOINT = 'https://gs1sso-dev.gs1.org/connect/'
OIDC_RP_PROVIDER_JWKS_ENDPOINT = "https://gs1sso-dev.gs1.org/.well-known/openid-configuration/jwks"
