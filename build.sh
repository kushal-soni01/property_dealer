#!/bin/bash
set -e

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r backend/requirements.txt

echo "Running Django migrations..."
cd backend/core
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Build completed successfully!"
