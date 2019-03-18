#!/bin/bash

echo "********************"
echo "* STARTING ${RUNTIME} on ${DJANGO_ENV}"
echo "********************"

#env

cd /root/app
echo "DJANGO_ENV=${DJANGO_ENV}" >> ./.env

if [[ $DJANGO_ENV = "staging" ]]
    then
    echo "DB: migrating ... ${RUNTIME} on ${DJANGO_ENV}"
    pipenv run python manage.py migrate
    pipenv run python manage.py loaddata ./fixtures/*
    make load
    make reload_templates
    echo "DB DONE ... "
fi

echo "staticfiles ... ${RUNTIME}"
#cd /root/app/deployment/scripts/ && bash install_frontend.sh
cd /root/app
pipenv run python manage.py collectstatic -v0 --no-input
chown -R www-data:www-data /home/www-data
cp /root/app/docker/nginx.conf /etc/nginx/

# docker localhost
if [[ $DJANGO_ENV = "staging" ]]
    then
    cd /etc/nginx/sites-available && rm * && ln -s /root/app/docker/default-local ./default
    cd /root/app && cat .env-localhost >> .env
fi

# docker azure staging
if [[ $DJANGO_ENV = "azure_swarm-stg" ]]
    then
    cd /etc/nginx/sites-available && rm * && ln -s /root/app/docker/default-stg ./default
    cd /root/app && cat .env-staging >> .env
fi

# docker azure produtcion
if [[ $DJANGO_ENV = "azure_swarm" ]]
    then
    cd /etc/nginx/sites-available && rm * && ln -s /root/app/docker/default ./default
    cd /root/app && cat .env-production >> .env
fi


service nginx restart


echo "creating superuser ${RUNTIME}"
cd /root/app && pipenv run python manage.py shell -c "
from django.contrib.auth.models import User
try:
    User.objects.create_superuser('admin2','admin2@example.com', 'pass2')
except:
    print('duplicate admin account')
    pass
"

#if ! [[ $DJANGO_ENV ~= *azure_swarm* ]]
#then
    echo "starting redis ${RUNTIME}"
    /usr/bin/redis-server /etc/redis/redis.conf
#fi

# if on azure link the locale directory (via azure volume)
LOCALE_DIRECTORY=/var/lib/activate/config/locale

# recreate just in case
mkdir -p /var/lib/activate/config/locale
mkdir -p /var/lib/activate/data/barcodes/bcgen
mkdir -p /var/lib/activate/data/media/product_images

# PRODUCTION
if [[ $DJANGO_ENV = "azure_swarm" ]]
    then
    mv /root/app/locale/ /root/app/_locale/ #move locale out of the way
    cd /var/lib/activate/config && rsync -v -ab --backup-dir=../locale_backup_`date +%F_%H%M%S` --delete --exclude=locale_backup_* /root/app/_locale/ locale
    cd /var/lib/activate/config && find . -type d -empty -delete #delete empty backups
    cd /home/www-data/staticfiles && mv ./bcgen ./_bcgen && ln -s /var/lib/activate/data/barcodes/bcgen
    # fix new relic environment
    perl -p -i.bak -e 's/development/production/g' /etc/supervisor/conf.d/gunicorn-django.conf
fi

# STAGING
if [[ $DJANGO_ENV = "azure_swarm-stg" ]]
    then
    mv /root/app/locale/ /root/app/_locale/ #move locale out of the way
    cd /var/lib/activate/config && rsync -v -ab --backup-dir=../locale_backup_`date +%F_%H%M%S` --delete --exclude=locale_backup_* /root/app/_locale/ locale
    cd /var/lib/activate/config && find . -type d -empty -delete #delete empty backups
    cd /home/www-data/staticfiles && mv ./bcgen ./_bcgen && ln -s /var/lib/activate/data/barcodes/bcgen
    perl -p -i.bak -e 's/development/staging/g' /etc/supervisor/conf.d/gunicorn-django.conf
fi

echo "all done"
