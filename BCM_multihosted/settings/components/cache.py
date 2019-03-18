CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/0',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'IGNORE_EXCEPTIONS': True,
        }
    },
    # db-1 is reserved for sessions, see components/sessions.py
    'api': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/2',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'IGNORE_EXCEPTIONS': True,
        },
        'TIMEOUT': 3600 * 24 * 1,  # 1 day
    }
}

REST_FRAMEWORK_CACHE = {
    'DEFAULT_CACHE_BACKEND': 'api',
    'DEFAULT_CACHE_TIMEOUT': CACHES['api']['TIMEOUT'],
}
