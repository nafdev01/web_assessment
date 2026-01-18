#!/bin/bash

# Exit on error
set -e

echo "Waiting for PostgreSQL to be ready..."
while ! pg_isready -h db -U ${POSTGRES_USER} -d ${POSTGRES_DB}; do
  sleep 1
done
echo "PostgreSQL is ready!"

echo "Waiting for Redis to be ready..."
while ! redis-cli -h redis ping > /dev/null 2>&1; do
  sleep 1
done
echo "Redis is ready!"

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Creating superuser if it doesn't exist..."
python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='${DJANGO_SUPERUSER_USERNAME:-admin}').exists():
    User.objects.create_superuser(
        username='${DJANGO_SUPERUSER_USERNAME:-admin}',
        email='${DJANGO_SUPERUSER_EMAIL:-admin@example.com}',
        password='${DJANGO_SUPERUSER_PASSWORD:-admin}'
    )
    print('Superuser created successfully')
else:
    print('Superuser already exists')
END

echo "Starting application..."
exec "$@"
