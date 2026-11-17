# ERP01 — Modular ERP v1.2.0

ERP01 is a Myanmar-aware business operations platform. The primary application
remains a Django REST Framework modular monolith for transactional inventory
and sales workflows. An optional FastAPI gateway and extracted Finance service
provide a controlled path toward the ARIMA-style service architecture.

## Implemented in this repository

### Core ERP application

- JWT sign-in, refresh, current-user endpoint and staff-only administration.
- Business profile with MMK, Asia/Yangon, and my-MM defaults.
- Customers and sales orders with draft, submitted, fulfilled and cancelled
  workflow states.
- Warehouses, categories, products, stock positions and stock movements.
- Immutable stock movement ledger; stock changes and ledger inserts share
  one transaction.
- Reserved-stock checks, database constraints and row-level locking for
  outbound movements.
- Order fulfilment deducts every line in one transaction. If any line is short,
  all stock changes and the order transition roll back.
- Live dashboard and operational CSV summary; sales totals are labelled as
  fulfilled order value, not cash receipts.

### Optional ARIMA-style service layer

- FastAPI gateway with a deployment-controlled service registry.
- Reverse proxy for the existing inventory, sales and core APIs.
- Extracted Finance module with Decimal amounts, staff-only JWT validation,
  atomic transfers, account-balance constraints and idempotency keys.
- Prometheus metrics and real dependency/module health probes.
- Optional Grafana, PostgreSQL exporter and Redis exporter services.

The gateway and Finance service are optional. ERP01 works without starting the
platform overlay. The Logistics, HR, E-commerce and SME services from the
proposed ARIMA layout are not enabled because their domain implementations
were not supplied; their placeholder directories are not reported as live
services.

## Technology

- Django 4.2 / Django REST Framework / SimpleJWT
- PostgreSQL 15
- Redis 7
- React 18 / Vite / Tailwind CSS
- Nginx
- Optional FastAPI / HTTPX / asyncpg / Prometheus / Grafana

## Start the core ERP stack

Requirements: Docker Engine and Docker Compose plugin.

~~~bash
cp .env.example .env
~~~

Generate a new SECRET_KEY (at least 50 random characters), set a unique
DB_PASSWORD, and set a unique GRAFANA_PASSWORD before using the optional
monitoring overlay. Set ALLOWED_HOSTS to the real hostnames for deployment.

~~~bash
docker compose config --quiet
docker compose up -d --build
docker compose ps
docker compose logs -f web
~~~

Create the first staff account explicitly:

~~~bash
docker compose exec web python src/manage.py createsuperuser
~~~

Open http://localhost:8080. The API is under /api/; Django Admin is under
/admin/.

## Start the optional gateway + Finance + monitoring layer

The Finance service validates the same SimpleJWT signatures as Django, so the
SECRET_KEY must be shared. It also checks the signed-in user against Django's
auth_user table and only permits active staff/superusers.

~~~bash
docker compose -f docker-compose.yml -f docker-compose.platform.yml config --quiet
docker compose -f docker-compose.yml -f docker-compose.platform.yml up -d --build
~~~

Default local-only endpoints:

| Service | URL |
|---|---|
| ERP web application | http://localhost:8080 |
| Gateway | http://127.0.0.1:8001 |
| Gateway health | http://127.0.0.1:8001/health |
| Registered modules | http://127.0.0.1:8001/modules |
| Finance module (through gateway) | http://127.0.0.1:8001/domains/finance/... |
| Prometheus | http://127.0.0.1:9090 |
| Grafana | http://127.0.0.1:3000 |

The gateway and monitoring UIs bind to loopback by default. Place an
authenticated TLS reverse proxy in front of any service that must be exposed.
PostgreSQL and Redis are not published to the host.

Example gateway requests (use an access token from /api/auth/token/):

~~~bash
curl http://127.0.0.1:8001/modules

curl -H "Authorization: Bearer $ACCESS_TOKEN" \
  http://127.0.0.1:8001/domains/inventory/products/

curl -H "Authorization: Bearer $ACCESS_TOKEN" \
  http://127.0.0.1:8001/domains/finance/balance/cash
~~~

The Finance transfer endpoint requires a unique Idempotency-Key header:

~~~bash
curl -X POST http://127.0.0.1:8001/domains/finance/transaction \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: transfer-2026-000001" \
  -d '{"from_account":"cash","to_account":"bank","amount":"25000.00","description":"Cash deposit"}'
~~~

Only staff users can create accounts, read account balances, review transfers,
and create transfers. An account must exist before it can participate in a
transfer. Currency conversion is not implemented; both accounts must use the
same currency. Create accounts via POST /domains/finance/accounts with a staff JWT.

## API overview

| Method | Endpoint | Purpose |
|---|---|---|
| POST | /api/auth/token/ | Obtain access / refresh tokens |
| POST | /api/auth/token/refresh/ | Refresh access token |
| GET | /api/auth/me/ | Current user and groups |
| GET | /api/health/ | Public database readiness probe |
| GET | /api/dashboard/ | Live dashboard metrics |
| GET / PATCH | /api/business-profile/ | Business settings; writes require staff |
| GET / POST | /api/inventory/products/ | Product management |
| POST | /api/inventory/stock-movements/adjust_stock/ | Post stock movement |
| GET / POST | /api/sales/customers/ | Customer management |
| GET / POST | /api/sales/orders/ | Order management |
| POST | /api/sales/orders/{id}/add_item/ | Add line to draft order |
| POST | /api/sales/orders/{id}/submit/ | Submit non-empty draft |
| POST | /api/sales/orders/{id}/fulfill/ | Atomic warehouse fulfilment |
| POST | /api/sales/orders/{id}/cancel/ | Cancel draft/submitted order |

Legacy inventory API paths such as /api/products/ remain available to avoid
breaking existing integrations.

## Quality checks

~~~bash
DJANGO_SETTINGS_MODULE=config.settings.test python src/manage.py check
DJANGO_SETTINGS_MODULE=config.settings.test python src/manage.py makemigrations --check --dry-run
pytest -o addopts=""
~~~

Frontend:

~~~bash
cd frontend
npm install
npm run build
~~~

Optional service dependencies and images:

~~~bash
pip install -r gateway/requirements.txt
pip install -r modules/finance/requirements.txt
docker build -t erp01-gateway:local gateway/
docker build -t erp01-finance:local modules/finance/
~~~

CI builds the Django, frontend, gateway and Finance images and runs Django
tests against PostgreSQL.

## Data safety

- docker compose down stops services but retains named volumes.
- Do not run docker compose down -v in an environment with business data.
- Back up PostgreSQL before applying production migrations.
- The stock reservation migration checks existing rows first and aborts with
  a reconciliation message rather than silently editing existing quantities.
- The Finance service owns idempotent SQL migrations under
  modules/finance/domain/migrations/.
- No secret values should be committed to Git.

## Scope and known boundaries

ERP01 v1.2.0 implements inventory and sales workflows and a limited Finance
transfer service. It does not yet implement full double-entry accounting,
payment settlement, customer debt allocation, branch tenancy, purchase
receiving, payroll, manufacturing, ecommerce checkout, or AI-agent execution.
Those capabilities must be implemented with domain-specific invariants and
tests before being advertised as available.
