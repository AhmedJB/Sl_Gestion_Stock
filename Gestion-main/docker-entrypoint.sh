#!/bin/bash
set -e

# Auto-migrate on container start / image rebuild
# Allows `docker build` + `docker run` without manual `manage.py migrate`

# Wait for DB if postgres (retry 30s)
echo "[entrypoint] Waiting for DB..."
for i in {1..30}; do
  python3 manage.py check --database default >/dev/null 2>&1 && break
  echo "  DB not ready, retry $i/30..."
  sleep 1
done

echo "[entrypoint] Running migrations..."
python3 manage.py migrate --noinput

# Optional: collect static (ignore failures if no static changes)
echo "[entrypoint] Collecting static..."
python3 manage.py collectstatic --noinput || true

echo "[entrypoint] Starting nginx..."
service nginx start

echo "[entrypoint] Starting gunicorn..."
exec gunicorn --bind 0.0.0.0:8000 gestionStock.wsgi
