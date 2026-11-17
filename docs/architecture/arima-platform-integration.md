# ARIMA-style service architecture in ERP01

## Decision

ERP01 keeps its Django application as the transactional system of record and
adds an optional FastAPI gateway plus an extracted Finance service. This is a
strangler-style transition: stable domain boundaries are introduced without
rewriting existing inventory and sales data or immediately creating a fleet
of partially implemented services.

## Current service topology

- web: Django REST Framework API and Django Admin. Owns customers, orders,
  products, warehouses, stock levels, stock movements, identity and business
  profile.
- gateway: FastAPI edge service. Routes only to deployment-configured upstreams.
  It does not accept service URLs from HTTP callers.
- finance: FastAPI service using the shared PostgreSQL instance. Owns its
  finance account and transfer tables in a dedicated namespace.
- postgres and redis: private backing services.
- prometheus and grafana: optional local-only observability surfaces.

The gateway maps:
- inventory -> Django /api/inventory/
- sales -> Django /api/sales/
- core -> Django /api/
- finance -> Finance /domains/finance/

The HTTP gateway does not mark a module online just because it is configured.
Its health endpoint probes the actual upstream health path and Redis ping.

## Corrections applied to the supplied ARIMA examples

1. **Async service discovery:** module lookup is synchronous against a static
   deployment-owned registry. The request path does not call an un-awaited
   coroutine or mutate the registry on every request.
2. **SSRF boundary:** no caller can register an arbitrary URL. Each service
   URL is read from environment configuration and checked for an HTTP(S)
   origin without embedded credentials, query strings or fragments.
3. **Proxy correctness:** the upstream URL preserves the configured base path
   and query string. Hop-by-hop headers and Connection-nominated headers are
   filtered. Upstream redirects are not followed. Timeouts and connection
   errors return bounded 504/502 responses instead of leaking exception text.
4. **Metrics cardinality:** metrics use FastAPI route templates after routing,
   not raw user-controlled paths or IDs.
5. **Real health reporting:** health checks probe Redis and each configured
   module; offline dependencies make the overall result degraded.
6. **Finance amount integrity:** amounts are Decimal values, transfers must be
   positive, accounts must differ, currencies must match, and insufficient
   balances are rejected.
7. **Concurrency and retries:** source/destination account rows are locked in
   deterministic order. Both balance writes and the journal record share one
   transaction. An idempotency key serializes retries and prevents the same
   transfer from being applied twice.
8. **Authorization:** Finance validates the Django SimpleJWT signature and
   requires an active staff/superuser record. The Finance container is not
   published to the host; the gateway is the internal route to it.
9. **No false WebSocket support:** WebSocket proxying is not enabled until a
   fully tested bidirectional implementation exists.
10. **No placeholder secrets:** production requires an explicit Django
    SECRET_KEY, database password and Grafana password.

## Module extraction policy

The Logistics, HR, E-commerce and SME services are not registered. Before
extracting another module, it must have:
- an owned domain model and migration strategy;
- explicit read/write ownership and transaction boundaries;
- authentication and role/permission rules;
- idempotency rules for retriable commands;
- health, metrics and structured logs;
- contract and end-to-end tests;
- a migration/cutover plan preserving existing records.

Do not split a transactional workflow across services without designing its
consistency strategy first. Inventory stock and sales order fulfilment remain
inside Django because those operations currently share one database
transaction.

## Security and operations

- Keep PostgreSQL, Redis, Finance and internal service ports on the private
  Compose network.
- Bind gateway, Prometheus and Grafana to loopback by default.
- Put external TLS and access policy at a trusted reverse proxy.
- Use the same Django SECRET_KEY in the Finance service to verify the same
  SimpleJWT tokens; rotate this secret as a coordinated deployment.
- Configure per-environment allowlisted service URLs. Do not accept arbitrary
  targets in a proxy request.
- Use docker compose down for routine shutdown. Removing named volumes is a
  destructive data operation and is not part of standard cleanup.
