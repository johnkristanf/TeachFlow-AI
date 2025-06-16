#!/bin/bash
set -e

echo "Running Alembic migrations..."
# Assuming alembic.ini is in the current working directory /app
# Or specify its path: alembic -c /app/alembic.ini upgrade head
alembic upgrade head

echo "Migrations completed. Starting FastAPI application..."
exec uvicorn main:app --host 0.0.0.0 --port 8000