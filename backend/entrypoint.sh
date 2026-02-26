#!/usr/bin/env sh
set -e
cd /app/cblxtool/

python manage.py migrate --noinput

gunicorn cblxtool.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 1 \
  --timeout 120
  --access-logfile - \
  --error-logfile - \
  --log-level debug
