RQ_QUEUES = {
    'default': {
        'HOST': '127.0.0.1',
        'PORT': 6379,
        'DB': 0,
        # 'PASSWORD': 'some-password',
        'DEFAULT_TIMEOUT': 360,
        'ASYNC': True,  # set to False if you want the "eager mode"
    },
}

# If you need custom exception handlers
# RQ_EXCEPTION_HANDLERS = ['path.to.my.handler']
