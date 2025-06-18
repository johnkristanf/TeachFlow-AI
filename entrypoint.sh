#!/bin/bash
set -e
echo "Running Alembic migrations..."
alembic upgrade head

echo "Migrations completed. Starting FastAPI application..."
exec uvicorn main:app --host 0.0.0.0 --port 8000 --lifespan on --log-config logging.ini