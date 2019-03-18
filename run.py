# gunicorn invocation
# from raven.contrib.flask import Sentry
# sentry = Sentry(dsn='https://3b27a3ff39bc4f8696840b9d5d661a0b:9a972467da084f29bf28a2473de871c4@app.getsentry.com/13007')

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "BCM_multihosted.settings")

application = get_wsgi_application()
