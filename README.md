
# Installation

## Perquisites

### Packages

  * brew install libjpeg
  * brew install imagemagick
  * brew install epstool

### Redis

  * brew install redis
  * brew services start redis

### Postgres

  * brew install postgres
  * /usr/local/opt/postgresql/bin/createuser -s postgres


## <a name="setup"></a> Setup code

### Prerequisites

   * pyenv https://github.com/pyenv/pyenv
   * pipenv: `python3 -m pip install -Iv pipenv==11.8.0`
   * docker
   * redis
### Setup

   * `git clone https://github.com/tbikeev/BCM_multihosted`
   * `cd BCM_multihosted`
   * `pipenv install`
   * `make test`, sames as `pipenv run python ./manage.py test`


### Local development
   * `pipenv run python ./manage.py migrate`
   * `pipenv run python ./manage.py test`
   * `pipenv run python manage.py loaddata ./fixtures/*`
   * `pipenv run python manage.py runserver`

## Setup DB

   * `pipenv run python ./manage.py migrate`

## Run app

   * `pipenv run python manage.py runserver`
   * http://localhost:8000/


# <a name="ci"></a>CI

- we will are moving to `pipenv` instead of requirements.txt, see `Pipfile` in `integration` branch
- we will use circleci.com as CI provider, on each commit, there will be some QA done, code linted, tests run etc, you would need to sign up with your gh id

## <a name="qa"></a>QA

- tests: `pipenv run python ./manage.py test`
- linting: `pip8`
- imports sort: `isort --recursive --check-only --diff <package> -sp tox.ini`, remove check-only to fix imports for you
- test coverage `pipenv run coverage run --source='.' manage.py test`
- coverage report `pipenv run coverage report`

# <a name="docker"></a>  Docker support

Docker support (including sshd, PG9.6, Redis, guncorn) is provided 


- `make docker_buid`  or `docker build  -t gs1go-activate:latest .`
- `make docker_run`  or `docker run -e DJANGO_ENV=staging -p 2222:22 -p 5050:5000 gs1go-activate`
- running ~~gunicorn~~ nginx is exposed on http://localhost:5050
- `make docker_ssh`  -- ssh into instance via: `cd ./docker && chmod 0700 ./id_rsa && ./docker_connect.sh`
- use `supervisorctl` on the docker host to stop-start gunicorn

# <a name="branches"></a>  Branches

- `integration` (protected) is used for merging (PRs only)
- `dev-*` are topical branches, used for development
- `production ` is used for production fixes

# <a name="branches"></a>  Gitflow
- use [gitflow](https://jeffkreeftmeijer.com/git-flow/) when possible

## Dependecnies

###  rest-framework-cache

```
pipenv uninstall rest-framework-cache
pipenv install git+https://github.com/tbikeev/django-rest-framework-cache.git@bc814fee117ce0a793ebc8679bba28f6c8b100aa#egg=rest-framework-cache
```

# Complete build steps

Note: 

- Build occurs on the development instance or deployment instance after successful `make test` has been run
- rosetta translations are needed to transferred and placed into `locales` directory before UI is compiled

## PRODUCTION environment

1. `make build_UI`
2. `make docker_build`
3. `make docker_push` (need to `docker login gs1go.azurecr.io -u gs1go -p DOCKER_REGISTRY_PASSWORD`
4. on the swarm manager `./deploy.sh`


## STAGING environment

1. `make build_UI`
2. `make docker_build-stg`
3. `make docker_push-stg` (need to `docker login gs1go.azurecr.io -u gs1go -p DOCKER_REGISTRY_PASSWORD`
4. on the swarm manager `./deploy-stg.sh`

# Run-time instrumentation

Both Staging and Production are instrumented with sentry.io listeners for python runtime and JS runtime.
Connection strings are specified in `RAVEN_CONFIG` sections in env settings.

# MO attributes (re)load

Note: MO attributes are first removed on the MO-by-MO basis, example:

`DJANGO_ENV=azure_swarm-stg  make reload_templates_es`
- 	`pipenv run python manage.py remove_templates gs1es` # remove MO templates and attributes first
- 	`pipenv run python manage.py load_templates_i18n "./deployment/deployment-v1-2018-03-products-dev/UI_presets_v2_templates_gs1es.xlsx"` # load specified MO spreadsheet



