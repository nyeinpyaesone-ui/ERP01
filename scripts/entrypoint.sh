#!/bin/sh
set -eu

: "${DB_HOST:=postgres}"
: "${DB_PORT:=5432}"
export DB_HOST DB_PORT
: "${DB_USER:?DB_USER must be set}"
: "${DB_NAME:?DB_NAME must be set}"
: "${DB_PASSWORD:?DB_PASSWORD must be set}"

echo "Waiting for PostgreSQL..."
python - <<'PY'
import os
import time
import psycopg2

for attempt in range(60):
    try:
        conn = psycopg2.connect(
            host=os.environ["DB_HOST"],
            port=os.getenv("DB_PORT", "5432"),
            dbname=os.environ["DB_NAME"],
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            connect_timeout=3,
        )
        conn.close()
        print("PostgreSQL is ready.")
        break
    except psycopg2.OperationalError:
        if attempt == 59:
            raise
        time.sleep(2)
PY

echo "Applying Django migrations..."
python src/manage.py migrate --noinput
echo "Collecting static assets..."
python src/manage.py collectstatic --noinput
echo "Starting ERP01 API..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --threads 2 \
    --timeout 60 \
    --max-requests 1000 \
    --max-requests-jitter 100
