bind = "127.0.0.1:5001"
accesslog = "/tmp/gunicorn-django-access.log"
errorlog  = "/tmp/gunicorn-django-error.log"
loglevel  = "debug"
max_requests = 0 # FIXME - remove in prod
pidfile = "/tmp/gunicorn-touch.pid"
