#!/bin/sh
set -e

python /app/manage.py migrate --noinput
python /app/manage.py compilemessages
yarn prod
python /app/manage.py collectstatic --noinput
