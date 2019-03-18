import raven

RAVEN_CONFIG = {
    'dsn': 'https://a711d95c7b174b9f8fff7d772a733a8a:39ae7ed779b34bcfb81befde5b09ad3c@sentry.io/303225',
    # If you are using git, you can also automatically configure the
    # release based on the git info.
    'release': raven.fetch_git_sha('/root/app'),
}

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'activate_v1',
        'USER': 'robot',
        'PASSWORD': 'robot',
    }
}

LOCALE_PATHS = (
    "/root/app/locale",
)

STATIC_ROOT = '/home/www-data/staticfiles'
BARCODES_FILES_PATH = '/home/www-data/staticfiles/bcgen'
MEDIA_ROOT = '/home/www-data/media'
PRODUCT_IMAGE_DIR = '/home/www-data/media/product_images'

BIN_CONVERT = '/usr/bin/convert'
BIN_COMPOSITE = '/usr/bin/composite'

DEBUG = True
