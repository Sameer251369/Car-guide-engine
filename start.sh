#!/usr/bin/env bash
set -e

python manage.py migrate --noinput
python manage.py seed_calculator_data
exec gunicorn carguide.wsgi:application