#!/bin/bash

WATCH_DIR=/var/lib/activate/config/locale
mkdir -p $WATCH_DIR

while true; do
    inotifywait \
        --exclude '.*\.py[co]$' \
        -e modify \
        -r $WATCH_DIR
    echo -n 'Restarting gunicorn ... '
    supervisorctl status gunicorn-django | sed "s/.*[pid ]\([0-9]\+\)\,.*/\1/" | xargs kill -HUP
    echo 'done'
done
