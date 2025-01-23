#!/bin/sh

CONTAINER_FIRST_STARTUP="CONTAINER_FIRST_STARTUP"
if [ ! -e /$CONTAINER_FIRST_STARTUP ]; then
    touch /$CONTAINER_FIRST_STARTUP

    echo "Waiting for database..."
    while ! nc -z db 5432; do
      sleep 0.1
    done


    alembic upgrade head && python -m app.seeds.run_seeds
    uvicorn app.main:app --host 0.0.0.0 --port 8000
else
    uvicorn app.main:app --host 0.0.0.0 --port 8000
fi