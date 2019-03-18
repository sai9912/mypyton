"""
This is a django-split-settings main file.
For more information read this:
https://github.com/sobolevn/django-split-settings
Default environment is `developement`.
To change settings file:
`DJANGO_ENV=production python manage.py runserver`
"""

from __future__ import print_function

import sys
from os import environ

from split_settings.tools import optional, include


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


django_env = environ.get('DJANGO_ENV', '').lower()
if django_env in ['development', 'localtest', 'production', 'staging',
                  'azure', 'azure_swarm', 'azure_swarm-stg',
                  'docker_local']:
    ENV = django_env
else:
    if __file__.startswith('/home/circleci/'):
    # if __file__.startswith('/home/alexei/'):
        ENV = 'circleci'
    elif len(sys.argv) > 1 and sys.argv[1] == 'test':
        ENV = 'localtest'
    else:
        ENV = 'development'
print('DJANGO_ENV=%s, ENV=%s' % (environ.get('DJANGO_ENV'), ENV))
# eprint('DJANGO ENV: %s' % ENV)

base_settings = [
    'components/base.py',  # standard django settings
    'components/database.py',  # postgres
    'components/cache.py',  # redis
    'components/task_queue.py',  # rq + django_rq
    'components/sessions.py',  # redis sessions settings

    # You can even use glob:
    # 'components/*.py'

    # Select the right env:
    'environments/%s.py' % ENV,

    # Optionally override some settings:
    optional('environments/local.py'),  # it seems it should be ".gitignore"d

    # place dev database settings here, it's under .gitignore
    optional('components/dev_database.py'),
]

# Include settings:
include(*base_settings)
