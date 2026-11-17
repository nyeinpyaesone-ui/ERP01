"""ARIMA-compatible gateway for ERP01's modular service boundaries."""

import logging
from contextlib import asynccontextmanager
from time import perf_counter

import httpx
import redis.asyncio as redis
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

from core.config import settings
from core.discovery import ServiceRegistry
from core.health import health_check
from core.proxy import RouteProxy

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REQUEST_COUNT = Counter(
    "erp_gateway_http_requests_total",
    "HTTP requests handled by the ERP gateway",
    ["method", "route", "status"],
)
REQUEST_LATENCY = Histogram(
    "erp_gateway_http_request_duration_seconds",
    "Gateway request latency in seconds",
    ["method", "route"],
)

registry = ServiceRegistry(settings.enabled_module_names())


@asynccontextmanager
async def lifespan(app: FastAPI):
    registry.load_from_environment()
    app.state.redis = redis.from_url(
        settings.redis_url,
        decode_responses=True,
        socket_connect_timeout=settings.health_timeout_seconds,
        socket_timeout=settings.health_timeout_seconds,
    )
    app.state.http = httpx.AsyncClient(
        timeout=httpx.Timeout(settings.request_timeout_seconds),
        limits=httpx.Limits(max_connections=200, max_keepalive_connections=40),
        follow_redirects=False,
        trust_env=False,
    )
    logger.info("Gateway ready with %d configured service routes.", len(registry.get_all()))
    try:
        yield
    finally:
        await app.state.http.aclose()
        await app.state.redis.aclose()


app = FastAPI(
    title="ERP01 Service Gateway",
    version="1.2.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.enable_api_docs else None,
    redoc_url=None,
    openapi_url="/openapi.json" if settings.enable_api_docs else None,
)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    started = perf_counter()
    response = await call_next(request)
    route = request.scope.get("route")
    route_label = getattr(route, "path", "unmatched")
    REQUEST_LATENCY.labels(
        method=request.method,
        route=route_label,
    ).observe(perf_counter() - started)
    REQUEST_COUNT.labels(
        method=request.method,
        route=route_label,
        status=str(response.status_code),
    ).inc()
    return response


@app.get("/health", tags=["operations"])
async def health(request: Request):
    result = await health_check(
        registry=registry,
        redis_client=request.app.state.redis,
        http_client=request.app.state.http,
        timeout_seconds=settings.health_timeout_seconds,
    )
    return JSONResponse(
        content=result,
        status_code=200 if result["status"] == "healthy" else 503,
    )


@app.get("/metrics", tags=["operations"])
async def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/modules", tags=["operations"])
async def list_modules():
    """Return configured service names, never internal service addresses."""
    return {"modules": registry.public_status()}


@app.api_route(
    "/domains/{module_name}/{path:path}",
    methods=["GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
)
async def route_to_module(module_name: str, path: str, request: Request):
    endpoint = registry.get(module_name)
    if endpoint is None:
        raise HTTPException(
            status_code=404,
            detail=f"Module '{module_name}' is not configured.",
        )

    proxy = RouteProxy(request.app.state.http)
    return await proxy.forward(request, endpoint.base_url, path)
