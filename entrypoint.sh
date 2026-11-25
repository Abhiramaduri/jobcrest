#!/bin/bash
set -e

echo "==> Running Django migrations..."
python manage.py migrate --noinput

echo "==> Collecting static files..."
python manage.py collectstatic --noinput

echo "==> Starting Gunicorn with Load Balancer header trust..."
WORKERS=${WEB_CONCURRENCY:-3}
THREADS=${GUNICORN_THREADS:-2}
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers "$WORKERS" \
    --threads "$THREADS" \
    --timeout 60 \
    --forwarded-allow-ips "*" \
    --access-logfile - \
    --error-logfile -
