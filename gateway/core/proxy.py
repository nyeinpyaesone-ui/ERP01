"""HTTP reverse proxy with hop-by-hop header filtering and bounded failures."""

import logging
import re
from urllib.parse import quote

import httpx
from fastapi import Request
from fastapi.responses import JSONResponse, StreamingResponse

logger = logging.getLogger(__name__)

HOP_BY_HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailer",
    "transfer-encoding",
    "upgrade",
}


class RouteProxy:
    def __init__(self, client: httpx.AsyncClient):
        self.client = client

    @staticmethod
    def _request_headers(request: Request) -> dict[str, str]:
        headers = dict(request.headers.items())
        connection_tokens = {
            token.strip().lower()
            for token in headers.get("connection", "").split(",")
            if token.strip()
        }
        excluded = HOP_BY_HOP_HEADERS | connection_tokens | {"host"}
        return {key: value for key, value in headers.items() if key.lower() not in excluded}

    @staticmethod
    def _response_headers(headers: httpx.Headers) -> dict[str, str]:
        connection_tokens = {
            token.strip().lower()
            for token in headers.get("connection", "").split(",")
            if token.strip()
        }
        excluded = HOP_BY_HOP_HEADERS | connection_tokens
        return {
            key: value
            for key, value in headers.items()
            if key.lower() not in excluded
        }

    async def forward(self, request: Request, target: str, path: str):
        segments = path.split("/")
        encoded_separator_or_dot = re.search(r"%(?:2e|2f|5c)", path, flags=re.IGNORECASE)
        if (
            path.startswith("/")
            or "\\" in path
            or encoded_separator_or_dot
            or any(segment in {".", ".."} for segment in segments)
        ):
            return JSONResponse({"detail": "Invalid upstream path."}, status_code=400)

        safe_path = quote(path, safe="/:@-._~!$&'()*+,;=")
        url = target.rstrip("/") + ("/" + safe_path if safe_path else "")
        if request.url.query:
            url += "?" + request.url.query

        upstream_request = self.client.build_request(
            method=request.method,
            url=url,
            headers=self._request_headers(request),
            content=await request.body(),
        )

        try:
            upstream = await self.client.send(upstream_request, stream=True)
        except httpx.TimeoutException:
            return JSONResponse({"detail": "Upstream service timed out."}, status_code=504)
        except httpx.RequestError:
            logger.warning("Upstream connection failed for gateway route.")
            return JSONResponse({"detail": "Upstream service is unavailable."}, status_code=502)

        async def stream_body():
            try:
                async for chunk in upstream.aiter_raw():
                    yield chunk
            finally:
                await upstream.aclose()

        return StreamingResponse(
            stream_body(),
            status_code=upstream.status_code,
            headers=self._response_headers(upstream.headers),
        )
