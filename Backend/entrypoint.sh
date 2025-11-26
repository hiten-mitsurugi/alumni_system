#!/bin/bash

# Exit on error
set -e

echo "🔄 Waiting for PostgreSQL..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.5
done
echo "✅ PostgreSQL is ready!"

echo "🔄 Waiting for Redis..."
while ! nc -z $REDIS_HOST $REDIS_PORT; do
  sleep 0.5
done
echo "✅ Redis is ready!"

echo "🔄 Running database migrations..."
python manage.py migrate --noinput --fake-initial 2>&1 || {
    echo "⚠️  Migration had conflicts, trying with --fake-initial..."
    python manage.py migrate --fake-initial --noinput
}

echo "📦 Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "🚀 Starting Daphne ASGI server..."
exec daphne -b 0.0.0.0 -p 8000 alumni_system.asgi:application
