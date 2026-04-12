#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Gather static files into the directory defined in STATIC_ROOT
python manage.py collectstatic --no-input

# Apply any outstanding database migrations
python manage.py migrate