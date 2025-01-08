#!/bin/sh
set -euo pipefail

echo "Executing database migration..."
alembic upgrade head
echo "Executing database migration done."

echo "Starting fastapi webserver with uvicorn..."
uvicorn "app.main:app" --reload --host 0.0.0.0
