import raven
from django.conf import settings
import os

print('+-------------------------+')
print('| Azure Swarm environment |')
print('+-------------------------+\n')

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
    'dsn': 'https://a711d95c7b174b9f8fff7d772a733a8a:39ae7ed779b34bcfb81befde5b09ad3c@sentry.io/303225',
    'release': raven_relase
}

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'activate_prod_v1',
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

# OIDC - prod
OIDC_RP_PROVIDER_ENDPOINT = 'https://gs1sso.gs1.org/connect/'
OIDC_RP_PROVIDER_JWKS_ENDPOINT = "https://gs1sso.gs1.org/.well-known/openid-configuration/jwks"
