"""Real dependency and upstream health probes."""

import asyncio
from datetime import datetime, timezone
from typing import Any

import httpx
from redis.asyncio import Redis

from .discovery import ServiceRegistry


async def health_check(
    registry: ServiceRegistry,
    redis_client: Redis,
    http_client: httpx.AsyncClient,
    timeout_seconds: float,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "status": "healthy",
        "gateway": "online",
        "redis": "unknown",
        "modules": {},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    try:
        await asyncio.wait_for(redis_client.ping(), timeout=timeout_seconds)
        result["redis"] = "online"
    except Exception:
        result["redis"] = "offline"
        result["status"] = "degraded"

    async def probe(name: str, endpoint) -> tuple[str, str]:
        try:
            response = await http_client.get(
                endpoint.health_url,
                timeout=timeout_seconds,
            )
            return name, "online" if response.is_success else "unhealthy"
        except Exception:
            return name, "offline"

    entries = registry.get_all().items()
    probes = await asyncio.gather(
        *(probe(name, endpoint) for name, endpoint in entries),
        return_exceptions=False,
    )
    for name, state in probes:
        result["modules"][name] = state
        if state != "online":
            result["status"] = "degraded"

    return result
