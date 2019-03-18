# Makefile (django)
#

.PHONY : clearscr fresh clean all

#
# Django
#
#

git_branch=$(shell git rev-parse --symbolic-full-name --abbrev-ref HEAD || echo "integration")
BUILD=version1

reset:
	- rm ./db.sqlite3
	pipenv run python manage.py migrate
	pipenv run python manage.py loaddata ./fixtures/*
	$(MAKE) add_admin

load:
	pipenv run python manage.py load_mo_user
	pipenv run python manage.py load_company_user

load-dev1: reset
	pipenv run python manage.py loaddata ./deployment/deployment-v1-2018-03-products-dev/default.json

load-dev2: reset load
	pipenv run python manage.py import_data ./deployment/deployment-v1-2018-03/sample_data.zip

load-dev3: reset load
	pipenv run python manage.py loaddata ./deployment/deployment-v1-2018-03-products-dev/attributes_v1.json
	pipenv run python manage.py loaddata ./deployment/deployment-v1-2018-03-products-dev/templates_v1.json

reload_templates:
	pipenv run python manage.py remove_templates gs1se
	pipenv run python manage.py remove_templates gs1ie
	pipenv run python manage.py remove_templates gs1bih
	pipenv run python manage.py remove_templates gs1go
	pipenv run python manage.py remove_templates gs1au
	pipenv run python manage.py load_templates_i18n "./deployment/deployment-v1-2018-03-products-dev/UI_presets_v2_templates_gs1ie.xlsx"
	pipenv run python manage.py load_templates_i18n "./deployment/deployment-v1-2018-03-products-dev/UI_presets_v2_templates_gs1se-5.xlsx"
	pipenv run python manage.py load_templates_i18n "./deployment/deployment-v1-2018-03-products-dev/UI_presets_v2_templates_gs1bih-5.xlsx"
	pipenv run python manage.py load_templates_i18n "./deployment/deployment-v1-2018-03-products-dev/UI_presets_v2_templates_gs1go.xlsx"
	pipenv run python manage.py load_templates_i18n "./deployment/deployment-v1-2018-03-products-dev/UI_presets_v2_templates_gs1au.xlsx"

reload_templates_fr:
	pipenv run python manage.py remove_templates gs1fr
	pipenv run python manage.py load_templates_i18n "./deployment/deployment-v1-2018-03-products-dev/UI_presets_v2_templates_gs1fr.xlsx"

reload_templates_es:
	pipenv run python manage.py remove_templates gs1es
	pipenv run python manage.py load_templates_i18n "./deployment/deployment-v1-2018-03-products-dev/UI_presets_v2_templates_gs1es.xlsx"

reload_templates_cz:
	pipenv run python manage.py remove_templates gs1cz
	pipenv run python manage.py load_templates_i18n "./deployment/deployment-v1-2018-03-products-dev/UI_presets_v2_templates_gs1cz-1.xlsx"

reload_templates_se:
	pipenv run python manage.py remove_templates gs1se
	pipenv run python manage.py load_templates_i18n "./deployment/deployment-v1-2018-03-products-dev/UI_presets_v2_templates_gs1se-5.xlsx"

build_ui:
	cd ./UI/vuejs/ && npm install
	cd ./UI/vuejs/ && npm run-script build
	pipenv run django-admin makemessages --ignore="locale.tmp" --ignore="static/site/js/standalone.js" --ignore="UI/vuejs/node_modules" --ignore="UI/node_modules" --ignore="UI/dist" -d djangojs -a

test:
	pipenv run python manage.py test

run: migrate
	pipenv run python manage.py runserver 127.0.0.1:8000

migrate:
	pipenv run python manage.py migrate

dumpdata:
	pipenv run python manage.py dumpdata --indent=4 --exclude contenttypes --exclude admin.logentry --exclude auth.permission \
		--exclude products \
		--exclude auth  \
		--exclude sessions \
		--exclude users \
		--exclude prefixes \
		--exclude audit  \
		--exclude company_organisations \
		--exclude member_organisations.MemberOrganisationUser \
		--exclude member_organisations.MemberOrganisationOwner \
		--indent 4 > fixtures/default.json

add_admin:
	echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@activate.org', 'pass')" | pipenv run python manage.py shell

add_frontend:
	cd ./deployment/scripts/ && BRANCH=$(git_branch) bash ./install_frontend.sh

sync_users:
	cp ../robot-gs1/deployment/deployment-v0-2018-01/mo_admins.json ./deployment/deployment-v1-2018-03/mo_admins.json
	cp ../robot-gs1/deployment/deployment-v0-2018-01/mo_users.json ./deployment/deployment-v1-2018-03/mo_users.json

rq:
	pipenv run python manage.py rqworker

#
# Docker
#

docker_build:
	docker build  -t gs1go-activate .
	docker tag gs1go-activate  gs1go.azurecr.io/gs1go-activate:1
	#docker tag gs1go-activate  gs1go.azurecr.io/gs1go-activate:latest

docker_build-stg:
	docker build  -t gs1go-activate-stg .
	docker tag gs1go-activate-stg  gs1go.azurecr.io/gs1go-activate-stg:1
	#docker tag gs1go-activate-stg  gs1go.azurecr.io/gs1go-activate-stg:latest

docker_run:
	- docker stop gs1-azure
	- docker rm   gs1-azure
	docker run --name=gs1-azure -e WEB_CONCURRENCY=10 -e DJANGO_ENV=staging -e BRANCH=$(git_branch) -p 2222:2222 -p 5050:5000 gs1go-activate

docker_run-stg:
	- docker stop gs1-azure
	- docker rm   gs1-azure
	docker run --name=gs1-azure -e WEB_CONCURRENCY=10 -e DJANGO_ENV=staging -e BRANCH=$(git_branch) -p 2222:2222 -p 5050:5000 gs1go-activate-stg

docker_kill:
	docker kill $(shell docker ps | grep 5050 | cut -f 1 -d " ")

docker_push:
	docker push   gs1go.azurecr.io/gs1go-activate:1
	#docker push   gs1go.azurecr.io/gs1go-activate:latest

docker_push-stg:
	docker push   gs1go.azurecr.io/gs1go-activate-stg:1
	#docker push   gs1go.azurecr.io/gs1go-activate-stg:latest

docker_ssh:
	chmod 0700 ./docker/id_rsa
	cd ./docker && ./docker_connect.sh

docker_test:
	chmod 0700 ./docker/id_rsa
	cd ./docker && ./docker_test.sh


### frontend

build-frontend:
	cd UI/vuejs/ && npm run-script build

build-frontend-dev:
	cd UI/vuejs/ && npm run-script build-dev

build-spa:
	cd ./UI/ && npm install
	cd ./UI/ && npm run buildForDjango

### translations

makemessages:
	django-admin makemessages --ignore="locale.tmp" --ignore="venv/*" --ignore="venv3/*" --ignore="static" -e "html,txt,py,rml"
	django-admin makemessages --ignore="locale.tmp" --ignore="static/site/js/standalone.js" --ignore="UI/vuejs/node_modules" --ignore="UI/node_modules" --ignore="UI/dist" -d djangojs -a
	django-admin compilemessages

### deployment

mk_release:
	.sentry/sentry-release-create.sh
	.sentry/sentry-release-add-commits.sh

release: mk_release docker_build docker_push

deploy:
	ssh manager0 -C /home/docker/deploy.sh
	.sentry/sentry-release-deploy.sh

# --

mk_release-stg:
	.sentry/sentry-release-create-stg.sh
	.sentry/sentry-release-add-commits-stg.sh

release-stg: mk_release-stg docker_build-stg docker_push-stg

deploy-stg:
	ssh manager0-stg -C /home/docker/deploy-stg.sh
	.sentry/sentry-release-deploy-stg.sh
