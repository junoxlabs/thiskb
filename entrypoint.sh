#!/bin/bash
set -euo pipefail

run_migrations() {
    echo "----------------- Applying database migrations -----------------"
    python manage.py makemigrations
    python manage.py migrate
}

collect_static() {
    echo "-----------------    collecting static files    -----------------"
    python manage.py collectstatic --noinput --clear
    python manage.py collectstatic --noinput
}

compress_static() {
    echo "-----------------   compressing static files   -----------------"
    python manage.py compress --force
}

if [ "${COLLECT_STATIC:-false}" = true ]; then
  collect_static
  compress_static
else
  echo "------------------ skipping collect static files -----------------"
fi


if [ "${RUN_MIGRATION:-false}" = true ]; then
    run_migrations
else
    echo "----------------- Skipping database migrations -----------------"
fi

echo "--------------------    Starting server    --------------------"
exec "$@"