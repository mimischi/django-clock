init:
	pip install pipenv --upgrade
	pipenv install --dev --skip-lock
ci:
	pipenv run pytest --cov=./
