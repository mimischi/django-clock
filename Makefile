init:
	pip install pipenv --upgrade
	pipenv install --dev --skip-lock
	yarn install --dev
	yarn build
ci:
	pipenv run pytest --cov=./
analyze:
	pipenv run flake8 .
	pipenv run isort -v
build:
	docker-compose build
rebuild:
	docker-compose build --force-rm --no-cache
lang-make:
	pipenv run python manage.py makemessages --no-location --no-wrap
lang-compile:
	pipenv run python manage.py compilemessages
