from django.conf import settings

print('+----------------------+')
print('| CircleCI environment |')
print('+----------------------+\n')

# components/cache.py
CACHES = settings.CACHES
CACHES['default']['LOCATION'] = 'redis://localhost:6379/0'
CACHES['api']['LOCATION'] = 'redis://localhost:6379/2'

# components/task_queue.py
RQ_QUEUES = settings.RQ_QUEUES
RQ_QUEUES['default']['HOST'] = 'localhost'
RQ_QUEUES['default']['PORT'] = 6379

# components/sessions.py
SESSION_REDIS = settings.SESSION_REDIS
SESSION_REDIS['host'] = 'localhost'
SESSION_REDIS['port'] = 6379
