init:
	pip install pipenv --upgrade
	pipenv install --dev --skip-lock
	yarn install --dev
	yarn build
ci:
	pipenv run pytest --cov=./
build:
	docker-compose build
rebuild:
	docker-compose build --force-rm --no-cache
lang-make:
	pipenv run python manage.py makemessages --no-location --no-wrap
lang-compile:
	pipenv run python manage.py compilemessages
