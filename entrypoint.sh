#!/bin/sh
set -e

export DJANGO_SETTINGS_MODULE="config.settings.prod"
export DJANGO_ENVIRONMENT_FILE=".env"

echo "Running migrations..."
uv run manage.py migrate

echo "Create initial data..."
uv run manage.py create_initial_data

exec "$@"
