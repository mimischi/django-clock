init:
	pip install pipenv --upgrade
	pipenv install --dev --skip-lock
	yarn install --dev
	yarn build
ci:
	pipenv run pytest --cov=./
build:
	docker-compose build
vbuild:
	docker-compose build --build-arg VERBOSE='--verbose' web
fbuild:
	docker-compose build --force-rm --no-cache
vfbuild:
	docker-compose build --force-rm --no-cache --build-arg VERBOSE='--verbose' web
lang-make:
	pipenv run python manage.py makemessages --no-location --no-wrap
lang-compile:
	pipenv run python manage.py compilemessages
