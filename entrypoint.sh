#!/bin/bash
set -e
echo "Running Alembic migrations..."
alembic -c alembic.ini --log-config logging.ini upgrade head

echo "Migrations completed. Starting FastAPI application..."
# Add the --log-config flag to the uvicorn command
exec uvicorn main:app --host 0.0.0.0 --port 8000 --lifespan on --log-config logging.ini