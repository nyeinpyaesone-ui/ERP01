# ERP01 v1.2.0 — Docker deployment

This repository is a Django 4.2 / Django REST Framework application. The
container configuration intentionally does not use the supplied Flask
run:app entrypoint, Flask migrations, port 5000, or backend/ build context.

## Services

- frontend: React/Vite production build served by Nginx on APP_PORT (default 8080).
- web: Django served by Gunicorn on private port 8000.
- postgres: PostgreSQL 15 with a persistent named volume.
- redis: Redis 7 with AOF persistence, private networking, and no-eviction
  policy for queued task data.

PostgreSQL and Redis are not published to the host. The browser calls
same-origin /api/ URLs; Nginx routes them to web:8000. This avoids exposing
Docker-internal DNS names to client-side JavaScript.

## First startup

Copy .env.example to .env.

Generate a new SECRET_KEY and set a unique DB_PASSWORD in .env. Set
ALLOWED_HOSTS to the public hostnames that will serve this deployment. Keep localhost, 127.0.0.1 and web in the list so container health checks and the internal gateway can reach Django.

    docker compose config
    docker compose up -d --build
    docker compose ps
    docker compose logs -f web

The web entrypoint waits for PostgreSQL, applies migrations, collects Django
static files into the persistent shared volume, and starts Gunicorn. The
frontend service waits for the Django health check before starting.

Create the initial staff account explicitly:

    docker compose exec web python src/manage.py createsuperuser

Open http://localhost:8080 (or the port in APP_PORT). Django Admin is
available at /admin/.

## Operations

    docker compose logs -f
    docker compose logs -f web
    docker compose exec web python src/manage.py check --deploy
    docker compose exec web python src/manage.py showmigrations
    docker compose exec postgres sh -c 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' > erp01-backup.sql

The database volume is persistent. docker compose down does not delete it.
Do not run docker compose down -v on an environment with business data:
that command removes the named database and Redis volumes.

For a public deployment, terminate TLS at a trusted reverse proxy and set
SECURE_SSL_REDIRECT=1 and an appropriate SECURE_HSTS_SECONDS only after
verifying forwarded-protocol handling. Restrict inbound network access to the
frontend entrypoint; keep database and Redis ports private.

The Redis service is only provisioned for internal queue/cache integration.
A running Redis container does not imply that background ERP workflows have
already been implemented or registered.
