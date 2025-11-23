# Render Backend Deployment Script
#!/bin/bash

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Running Django migrations..."
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Django application with Daphne..."
daphne -b 0.0.0.0 -p $PORT alumni_system.asgi:application