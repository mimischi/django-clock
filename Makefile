.PHONY: init version ci analyze build rebuild lang-make lang-compile clean-pyc

init:
	pip install pipenv --upgrade
	pipenv install --dev --skip-lock
	yarn install --dev
	yarn build
version:
	pipenv run flake8 --version
	pipenv run isort --version
	black --version
ci:
	pipenv run pytest --cov=./
analyze:
	pipenv run flake8 .
	pipenv run isort --check-only
	black --check clock/ config/ manage.py
build:
	docker-compose build
rebuild:
	docker-compose build --force-rm --no-cache
lang-make:
	pipenv run python manage.py makemessages --no-location --no-wrap
lang-compile:
	pipenv run python manage.py compilemessages
clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -rf {} +
