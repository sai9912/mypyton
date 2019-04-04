# VERSION               0.1.1

FROM      arwineap/docker-ubuntu-python3.6
MAINTAINER Thomas Bikeev thomas.bikeev@mac.com

# make sure the package repository is up to date
# add generic reqs

RUN apt-get update
RUN apt-get install -y openssh-server curl vim python supervisor python-setuptools python-simplejson python-imaging sqlite3 git-core gcc python-dev \
			libsqlite3-dev imagemagick make openssh-client redis-server rsyslog nginx software-properties-common python-software-properties python3.6-dev

# other repositories
RUN add-apt-repository ppa:git-core/ppa

RUN apt-get update
RUN apt-get install -y locales && localedef -i en_US \
    -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8

RUN apt-get update
RUN LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8 DEBIAN_FRONTEND=noninteractive \
    apt-get install -y -q postgresql-9.5 postgresql-contrib-9.5 postgresql-server-dev-9.5

# -- postgres setup
# prevent apt from starting postgres right after the installation
RUN	echo "#!/bin/sh\nexit 101" > /usr/sbin/policy-rc.d; chmod +x /usr/sbin/policy-rc.d
ENV LANGUAGE en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LC_ALL en_US.UTF-8
RUN DEBIAN_FRONTEND=noninteractive locale-gen en_US.UTF-8
RUN DEBIAN_FRONTEND=noninteractive dpkg-reconfigure locales
RUN update-locale LANG=en_US.UTF-8
USER postgres
RUN /etc/init.d/postgresql start \
    && psql --command "CREATE USER pguser WITH SUPERUSER PASSWORD 'postgres';" \
    && psql --command "CREATE USER robot  WITH SUPERUSER PASSWORD 'robot';" \
    && createdb -O postgres -E UTF8 -T template0 --locale=en_US.utf8 activate_v1 \
    && psql --command "GRANT ALL PRIVILEGES ON DATABASE activate_v1 to robot;"
USER root
RUN echo "local all all trust"   > /etc/postgresql/9.5/main/pg_hba.conf
#RUN echo "listen_address = '' " >> /etc/postgresql/9.5/main/postgresql.conf
RUN echo "listen_addresses='*'" >> /etc/postgresql/9.5/main/postgresql.conf
RUN echo "client_encoding = utf8" >> /etc/postgresql/9.5/main/postgresql.conf
RUN mkdir -p /var/run/postgresql && chown -R postgres /var/run/postgresql
VOLUME  ["/etc/postgresql", "/var/log/postgresql", "/var/lib/postgresql"]
# allow autostart again
USER root
RUN	rm /usr/sbin/policy-rc.d

# -- redis setup
RUN /usr/bin/redis-server /etc/redis/redis.conf

# -- epstool setup
ADD ./src /root/app/src
RUN cd /root/app/src && ./install_epstool.sh > /dev/null 2>/dev/null

# --node setup
# nvm environment variables
ENV NVM_DIR /usr/local/nvm
ENV NODE_VERSION 8.11.1

# install nvm
# https://github.com/creationix/nvm#install-script
RUN curl --silent -o- https://raw.githubusercontent.com/creationix/nvm/v0.31.2/install.sh | bash

# install node and npm
RUN . $NVM_DIR/nvm.sh \
    && nvm install $NODE_VERSION \
    && nvm alias default $NODE_VERSION \
    && nvm use default

# add node and npm to path so the commands are available
ENV NODE_PATH $NVM_DIR/v$NODE_VERSION/lib/node_modules
ENV PATH $NVM_DIR/versions/node/v$NODE_VERSION/bin:$PATH

# confirm installation
RUN node -v
RUN npm -v

# open office
RUN apt-get install -y libreoffice --no-install-recommends

# inotify tools
RUN apt-get install -y inotify-tools

# dropbox setup
# RUN cd ~ && wget -O - "https://www.dropbox.com/download?plat=lnx.x86_64" | tar xzf -

# timber setup
 RUN curl -o /opt/timber-agent.tar.gz https://packages.timber.io/agent/0.6.x/linux-amd64/timber-agent-0.6.x-linux-amd64.tar.gz
 RUN cd /opt && tar -xzf timber-agent.tar.gz && rm timber-agent.tar.gz
 RUN cp /opt/timber-agent/support/config/timber.basic.toml /etc/timber.toml
 ADD ./docker/timber.toml /etc/timber.toml

#RUN cd /usr/local/bin \
#  && ln -s /usr/bin/python3 python \
#  && pip3 install --upgrade pip

#expose ports
EXPOSE 22
EXPOSE 5000
EXPOSE 8000
EXPOSE 2222 80


# ------------------------
# SSH Server support
# ------------------------
USER root
ADD ./docker/id_rsa.pub /etc/ssh/authorized_keys2
RUN chmod 700    /etc/ssh/authorized_keys2
RUN chown root   /etc/ssh/authorized_keys2
RUN echo "root:Docker!" | chpasswd
ADD ./docker/rsyslog.conf /etc/rsyslog.conf

#checkout the app
#RUN ssh-add ./.ssh/id_dsa;
#RUN git clone -b master git@github.com:tbikeev/odb-ddr-unit-02.git

#python set-up
RUN pip3 install -Iv pipenv==11.6.3
ADD ./Pipfile                       /root/app/Pipfile
ADD ./Pipfile.lock                  /root/app/Pipfile.lock
RUN cd /root/app && pipenv install

#app setup
ADD ./BCM                           /root/app/BCM
ADD ./BCM_multihosted               /root/app/BCM_multihosted
ADD ./audit                         /root/app/audit
ADD ./barcodes                      /root/app/barcodes
ADD ./bin                           /root/app/bin
ADD ./cloud                         /root/app/cloud
ADD ./company_organisations         /root/app/company_organisations
ADD ./core.py                       /root/app/core.py
ADD ./deployment                    /root/app/deployment
ADD ./docker                        /root/app/docker
ADD ./fixtures                      /root/app/fixtures
ADD ./activate                      /root/app/activate
ADD ./locale                        /root/app/locale
ADD ./media                         /root/app/media
ADD ./manage.py                     /root/app/manage.py
ADD ./member_organisations          /root/app/member_organisations
ADD ./prefixes                      /root/app/prefixes
ADD ./products                      /root/app/products
ADD ./service.py                    /root/app/service.py
ADD ./services.py                   /root/app/services.py
ADD ./static                        /root/app/static
ADD ./templates                     /root/app/templates
ADD ./tox.ini                       /root/app/tox.ini
ADD ./users                         /root/app/users
ADD ./excel                         /root/app/excel
ADD ./frontend                      /root/app/frontend
ADD ./api                           /root/app/api
#ADD ./UI                            /root/app/UI
ADD ./utils                         /root/app/utils
ADD ./oidc_gs1                      /root/app/oidc_gs1
ADD ./Makefile                      /root/app/Makefile
ADD ./run.py                        /root/app/run.py

#ADD ./.env                          /root/app/.env
#ADD ./.env-localhost                /root/app/.env-localhost
#ADD ./.env-staging                  /root/app/.env-staging
#ADD ./.env-production               /root/app/.env-production

# revision
ADD ./.git                          /root/app/.git

# add ssl
ADD ./activate_gs1_org/combined-activate_gs1_org.ca-bundle /etc/ssl/certs/combined-activate_gs1_org.ca-bundle
#ADD ./activate_gs1_org/activate_gs1_org.key  /etc/ssl/private/activate_gs1_org.key

ADD ./activate_gs1_org/combined-activate_gs1_org-stg.ca-bundle /etc/ssl/certs/combined-activate_gs1_org-stg.ca-bundle
#ADD ./activate_gs1_org/activate_gs1_org-stg.key  /etc/ssl/private/activate_gs1_org-stg.key


# app directories
RUN mkdir -p /root/app/logs/
RUN mkdir -p /root/app/conf/
RUN mkdir -p /var/run/sshd/ # for sshd

#setup supervisor
ADD ./docker/gunicorn-django.conf   /etc/supervisor/conf.d/gunicorn-django.conf
ADD ./docker/rq.conf                /etc/supervisor/conf.d/rq.conf

#call start command
ADD ./docker/sshd_config /etc/ssh/sshd_config
ADD ./docker/supervisor.conf /etc/supervisor/conf.d/supervisor.conf

ENTRYPOINT /etc/init.d/postgresql start && /root/app/docker/start-all.sh && supervisord -n

