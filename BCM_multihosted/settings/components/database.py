import os

from pathlib import Path

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases


DB_BASE_DIR = Path(__file__).parents[2]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(DB_BASE_DIR, 'db.sqlite3'),
    }
}
