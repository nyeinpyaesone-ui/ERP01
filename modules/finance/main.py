"""Standalone finance service that can be routed by the ERP01 gateway."""

import logging
import os
from contextlib import asynccontextmanager
from time import perf_counter
from pathlib import Path

import asyncpg
from fastapi import FastAPI, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest

from domain.routes import router

logger = logging.getLogger(__name__)
REQUEST_COUNT = Counter(
    "erp_finance_requests_total",
    "Requests served by the finance module",
    ["method", "endpoint", "status"],
)


async def apply_migrations(pool):
    migration_dir = Path(__file__).resolve().parent / "domain" / "migrations"
    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS finance_schema_migrations (
                    name VARCHAR(200) PRIMARY KEY,
                    applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
                """
            )
            for migration in sorted(migration_dir.glob("*.sql")):
                applied = await conn.fetchval(
                    "SELECT 1 FROM finance_schema_migrations WHERE name = $1",
                    migration.name,
                )
                if applied:
                    continue
                await conn.execute(migration.read_text(encoding="utf-8"))
                await conn.execute(
                    "INSERT INTO finance_schema_migrations (name) VALUES ($1)",
                    migration.name,
                )


@asynccontextmanager
async def lifespan(app: FastAPI):
    secret = os.getenv("SECRET_KEY")
    required = ["DB_HOST", "DB_NAME", "DB_USER", "DB_PASSWORD"]
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        raise RuntimeError("Missing required finance environment configuration: " + ", ".join(missing))
    if not secret or len(secret) < 32:
        raise RuntimeError("SECRET_KEY must be shared with Django and contain at least 32 characters.")

    pool = await asyncpg.create_pool(
        host=os.environ["DB_HOST"],
        port=int(os.getenv("DB_PORT", "5432")),
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"],
        min_size=1,
        max_size=int(os.getenv("DB_POOL_MAX_SIZE", "10")),
        command_timeout=30,
    )
    await apply_migrations(pool)
    app.state.db = pool
    logger.info("Finance service started and schema migrations checked.")
    try:
        yield
    finally:
        await pool.close()


app = FastAPI(
    title="ERP01 Finance Module",
    version="1.2.0",
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)
app.include_router(router, prefix="/domains/finance")


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    started = perf_counter()
    response = await call_next(request)
    route = request.scope.get("route")
    endpoint = getattr(route, "path", "unmatched")
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=endpoint,
        status=str(response.status_code),
    ).inc()
    return response


@app.get("/health", tags=["operations"])
async def health():
    try:
        await app.state.db.fetchval("SELECT 1")
        return {"status": "healthy", "module": "finance", "database": "online"}
    except Exception:
        return Response(
            content='{"status":"degraded","module":"finance","database":"offline"}',
            status_code=503,
            media_type="application/json",
        )


@app.get("/metrics", tags=["operations"])
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/", tags=["operations"])
async def root():
    return {"module": "finance", "version": "1.2.0", "status": "operational"}
